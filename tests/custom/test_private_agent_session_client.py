import types

from truefoundry_gateway_sdk.agents.agent_session import AgentSession
from truefoundry_gateway_sdk.agents.prepared_turn import PreparedTurn
from truefoundry_gateway_sdk.agents.private import AgentDraftSession, PrivateAgentSessionClient
from truefoundry_gateway_sdk.agents.turn import Turn
from truefoundry_gateway_sdk.core.pagination import SyncPager
from truefoundry_gateway_sdk.types.agent_spec import AgentSpec
from truefoundry_gateway_sdk.types.draft_session import DraftSession as RawDraftSession
from truefoundry_gateway_sdk.types.model import Model
from truefoundry_gateway_sdk.types.session import Session as RawSession
from truefoundry_gateway_sdk.types.subject import Subject
from truefoundry_gateway_sdk.types.turn import Turn as RawTurn
from truefoundry_gateway_sdk.types.turn_state_running import TurnStateRunning

SUBJECT = Subject(subject_id="subject_id", subject_type="subject_type", subject_slug="subject_slug")

RAW_SESSION = RawSession(
    id="session-1",
    agent_name="agent_name",
    title="a session",
    created_by_subject=SUBJECT,
    created_at="2026-01-01T00:00:00Z",
    updated_at="2026-01-01T00:00:00Z",
)

RAW_DRAFT = RawDraftSession(
    id="draft-1",
    agent_spec=AgentSpec(model=Model(name="gpt-4o")),
    agent_name="agent_name",
    title="a draft",
    created_by_subject=SUBJECT,
    created_at="2026-01-01T00:00:00Z",
    updated_at="2026-01-01T00:00:00Z",
)


def _new_client() -> PrivateAgentSessionClient:
    return PrivateAgentSessionClient(base_url="https://example.com", api_key="test", max_retries=0)


def _pager(items, *, next_pager=None):
    return SyncPager(
        get_next=(lambda: next_pager) if next_pager is not None else None,
        has_next=next_pager is not None,
        items=items,
        response=None,
    )


def test_list_owned_sessions_wraps_each_member_by_discriminant(monkeypatch):
    client = _new_client()
    raw_private = client._client.agents.private
    monkeypatch.setattr(raw_private, "list_owned_sessions", lambda **kw: _pager([RAW_SESSION, RAW_DRAFT]))

    items = list(client.list_owned_sessions())
    assert len(items) == 2

    session, draft = items
    assert isinstance(session, AgentSession)
    assert session.type == "session"
    assert session.id == "session-1"

    assert isinstance(draft, AgentDraftSession)
    assert draft.type == "session/draft"
    assert draft.id == "draft-1"
    assert draft.agent_spec.model.name == "gpt-4o"


def test_list_owned_sessions_paginates_via_next_page_token(monkeypatch):
    client = _new_client()
    raw_private = client._client.agents.private
    page2 = _pager([RAW_SESSION])
    monkeypatch.setattr(raw_private, "list_owned_sessions", lambda **kw: _pager([RAW_SESSION], next_pager=page2))

    page = client.list_owned_sessions(limit=1)
    assert page.has_next is True
    next_page = page.get_next()
    assert next_page is not None
    assert isinstance(next_page.items[0], AgentSession)


def test_list_draft_sessions_wraps_each_raw_draft(monkeypatch):
    client = _new_client()
    raw_drafts = client._client.agents.private.draft_sessions
    monkeypatch.setattr(raw_drafts, "list", lambda **kw: _pager([RAW_DRAFT]))

    items = list(client.list_draft_sessions())
    assert len(items) == 1
    assert isinstance(items[0], AgentDraftSession)
    assert items[0].id == "draft-1"


def test_prepare_turn_returns_prepared_turn_without_request(monkeypatch):
    client = _new_client()
    raw_private = client._client.agents.private
    monkeypatch.setattr(raw_private, "list_owned_sessions", lambda **kw: _pager([RAW_DRAFT]))

    (draft,) = list(client.list_owned_sessions())
    prepared = draft.prepare_turn()
    assert isinstance(prepared, PreparedTurn)
    assert prepared.session is draft
    assert isinstance(prepared.session, AgentDraftSession)
    assert prepared.session.agent_name == "agent_name"


def test_get_turn_session_is_enriched_owner(monkeypatch):
    client = _new_client()
    raw_private = client._client.agents.private
    monkeypatch.setattr(raw_private, "list_owned_sessions", lambda **kw: _pager([RAW_SESSION]))

    raw_turn = RawTurn(
        id="turn-1",
        session_id="session-1",
        created_by_subject=SUBJECT,
        created_at="2026-01-01T00:00:00Z",
        state=TurnStateRunning(),
    )
    raw_turns = client._client.agents.sessions
    monkeypatch.setattr(raw_turns, "get_turn", lambda session_id, turn_id, **kw: types.SimpleNamespace(data=raw_turn))

    (session,) = list(client.list_owned_sessions())
    turn = session.get_turn("turn-1")
    assert isinstance(turn, Turn)
    assert turn.session is session
    assert isinstance(turn.session, AgentSession)
    assert turn.session.agent_name == "agent_name"
    assert turn.session.title == "a session"


def test_draft_session_update_mutates_agent_spec_and_updated_at_in_place(monkeypatch):
    client = _new_client()
    raw_private = client._client.agents.private
    monkeypatch.setattr(raw_private, "list_owned_sessions", lambda **kw: _pager([RAW_DRAFT]))

    (draft,) = list(client.list_owned_sessions())
    assert draft.agent_spec.model.name == "gpt-4o"
    assert draft.updated_at == "2026-01-01T00:00:00Z"

    new_spec = AgentSpec(model=Model(name="gpt-4.1"))
    updated_raw = RawDraftSession(
        id="draft-1",
        agent_spec=new_spec,
        agent_name="agent_name",
        title="a draft",
        created_by_subject=SUBJECT,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-02-01T00:00:00Z",
    )
    recorded_calls = []

    def fake_update(draft_session_id, *, agent_spec=None, request_options=None):
        recorded_calls.append((draft_session_id, agent_spec))
        return types.SimpleNamespace(data=updated_raw)

    monkeypatch.setattr(raw_private.draft_sessions, "update", fake_update)

    result = draft.update(agent_spec=new_spec)
    assert result is None
    assert recorded_calls == [("draft-1", new_spec)]
    assert draft.agent_spec.model.name == "gpt-4.1"
    assert draft.updated_at == "2026-02-01T00:00:00Z"


def test_download_sandbox_file_delegates_to_raw_client(monkeypatch):
    client = _new_client()
    raw_private = client._client.agents.private
    recorded_calls = []

    def fake_download(sandbox_id, *, path, request_options=None):
        recorded_calls.append((sandbox_id, path))
        return iter([b"hello", b"world"])

    monkeypatch.setattr(raw_private, "download_sandbox_file", fake_download)

    chunks = list(client.download_sandbox_file("sandbox-1", path="/tmp/out.txt"))
    assert chunks == [b"hello", b"world"]
    assert recorded_calls == [("sandbox-1", "/tmp/out.txt")]
