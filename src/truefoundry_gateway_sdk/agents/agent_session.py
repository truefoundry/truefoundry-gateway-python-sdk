import typing

from ..core.pagination import AsyncPager, SyncPager
from ..core.request_options import RequestOptions
from ..types.list_turns_response import ListTurnsResponse
from ..types.previous_turn_id_input import PreviousTurnIdInput
from ..types.session import Session as RawSession
from ..types.subject import Subject
from ..types.turn import Turn as RawTurn
from ..types.turn_input_item import TurnInputItem
from .prepared_turn import AsyncPreparedTurn, PreparedTurn
from .turn import AsyncTurn, Turn


def _wrap_turns_pager(
    raw_pager: SyncPager[RawTurn, ListTurnsResponse],
    session: "AgentSession",
    client: typing.Any,
) -> SyncPager[Turn, ListTurnsResponse]:
    wrapped_items = [Turn(t, session, client) for t in (raw_pager.items or [])]

    def get_next() -> typing.Optional[SyncPager[Turn, ListTurnsResponse]]:
        if raw_pager.get_next is None:
            return None
        next_raw = raw_pager.get_next()
        if next_raw is None:
            return None
        return _wrap_turns_pager(next_raw, session, client)

    return SyncPager(
        get_next=get_next if raw_pager.has_next else None,
        has_next=raw_pager.has_next,
        items=wrapped_items,
        response=raw_pager.response,
    )


async def _async_wrap_turns_pager(
    raw_pager: AsyncPager[RawTurn, ListTurnsResponse],
    session: "AsyncAgentSession",
    client: typing.Any,
) -> AsyncPager[AsyncTurn, ListTurnsResponse]:
    wrapped_items = [AsyncTurn(t, session, client) for t in (raw_pager.items or [])]

    async def get_next() -> typing.Optional[AsyncPager[AsyncTurn, ListTurnsResponse]]:
        if raw_pager.get_next is None:
            return None
        next_raw = await raw_pager.get_next()
        if next_raw is None:
            return None
        return await _async_wrap_turns_pager(next_raw, session, client)

    return AsyncPager(
        get_next=get_next if raw_pager.has_next else None,
        has_next=raw_pager.has_next,
        items=wrapped_items,
        response=raw_pager.response,
    )


class AgentSession:
    """
    A session enriched with convenience methods: prepare_turn, list_turns, get_turn, cancel.
    """

    def __init__(self, session: RawSession, client: typing.Any) -> None:
        self._id: str = session.id
        self._agent_name: str = session.agent_name
        self._title: typing.Optional[str] = session.title
        self._created_by_subject: Subject = session.created_by_subject
        self._created_at: str = session.created_at
        self._updated_at: str = session.updated_at
        self._client = client

    def __repr__(self) -> str:
        return f"AgentSession(id={self._id!r}, agent_name={self._agent_name!r})"

    @property
    def id(self) -> str:
        return self._id

    @property
    def agent_name(self) -> str:
        return self._agent_name

    @property
    def title(self) -> typing.Optional[str]:
        return self._title

    @property
    def created_by_subject(self) -> Subject:
        return self._created_by_subject

    @property
    def created_at(self) -> str:
        return self._created_at

    @property
    def updated_at(self) -> str:
        return self._updated_at

    def prepare_turn(
        self,
        *,
        input: typing.Optional[typing.Sequence[TurnInputItem]] = None,
        previous_turn_id: typing.Optional[PreviousTurnIdInput] = None,
    ) -> PreparedTurn:
        """Stage a turn locally (no HTTP). Omit ``previous_turn_id`` to chain to the session's last turn (server default ``auto``). Call ``execute()`` once to start ``create_turn``."""
        return PreparedTurn(
            input=input,
            previous_turn_id=previous_turn_id,
            session=self,
            client=self._client,
        )

    def list_turns(
        self,
        *,
        page_token: typing.Optional[str] = None,
        limit: typing.Optional[int] = 10,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SyncPager[Turn, ListTurnsResponse]:
        """List turns in this session."""
        raw_pager = self._client.agents.sessions.list_turns(
            self._id, page_token=page_token, limit=limit, request_options=request_options
        )
        return _wrap_turns_pager(raw_pager, self, self._client)

    def get_turn(
        self,
        turn_id: str,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> Turn:
        """Fetch a turn by ID."""
        response = self._client.agents.sessions.get_turn(self._id, turn_id, request_options=request_options)
        return Turn(response.data, self, self._client)

    def cancel(self, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        """Cancel the running last turn for the session."""
        self._client.agents.sessions.cancel(self._id, request_options=request_options)


class AsyncAgentSession:
    """
    Async version of AgentSession.
    """

    def __init__(self, session: RawSession, client: typing.Any) -> None:
        self._id: str = session.id
        self._agent_name: str = session.agent_name
        self._title: typing.Optional[str] = session.title
        self._created_by_subject: Subject = session.created_by_subject
        self._created_at: str = session.created_at
        self._updated_at: str = session.updated_at
        self._client = client

    def __repr__(self) -> str:
        return f"AsyncAgentSession(id={self._id!r}, agent_name={self._agent_name!r})"

    @property
    def id(self) -> str:
        return self._id

    @property
    def agent_name(self) -> str:
        return self._agent_name

    @property
    def title(self) -> typing.Optional[str]:
        return self._title

    @property
    def created_by_subject(self) -> Subject:
        return self._created_by_subject

    @property
    def created_at(self) -> str:
        return self._created_at

    @property
    def updated_at(self) -> str:
        return self._updated_at

    def prepare_turn(
        self,
        *,
        input: typing.Optional[typing.Sequence[TurnInputItem]] = None,
        previous_turn_id: typing.Optional[PreviousTurnIdInput] = None,
    ) -> AsyncPreparedTurn:
        """Stage a turn locally (no HTTP). Omit ``previous_turn_id`` to chain to the session's last turn (server default ``auto``). Call ``execute()`` once to start ``create_turn``."""
        return AsyncPreparedTurn(
            input=input,
            previous_turn_id=previous_turn_id,
            session=self,
            client=self._client,
        )

    async def list_turns(
        self,
        *,
        page_token: typing.Optional[str] = None,
        limit: typing.Optional[int] = 10,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncPager[AsyncTurn, ListTurnsResponse]:
        """List turns in this session."""
        raw_pager = await self._client.agents.sessions.list_turns(
            self._id, page_token=page_token, limit=limit, request_options=request_options
        )
        return await _async_wrap_turns_pager(raw_pager, self, self._client)

    async def get_turn(
        self,
        turn_id: str,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncTurn:
        """Fetch a turn by ID."""
        response = await self._client.agents.sessions.get_turn(self._id, turn_id, request_options=request_options)
        return AsyncTurn(response.data, self, self._client)

    async def cancel(self, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        """Cancel the running last turn for the session."""
        await self._client.agents.sessions.cancel(self._id, request_options=request_options)
