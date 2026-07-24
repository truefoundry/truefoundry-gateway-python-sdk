from __future__ import annotations

import typing

from ...private.agents.private.draft_sessions.client import OMIT
from ..session_mixin import AsyncSessionMixin, SessionMixin

if typing.TYPE_CHECKING:
    from ...client import AsyncTrueFoundryGateway, TrueFoundryGateway
    from ...core.pagination import AsyncPager, SyncPager
    from ...core.request_options import RequestOptions
    from ...types.agent_spec import AgentSpec
    from ...types.draft_session import DraftSession as RawDraftSession
    from ...types.list_session_events_response import ListSessionEventsResponse
    from ...types.list_turns_response import ListTurnsResponse
    from ...types.previous_turn_id_input import PreviousTurnIdInput
    from ...types.session_event_item import SessionEventItem
    from ...types.subject import Subject
    from ...types.turn_input_item import TurnInputItem
    from ..prepared_turn import AsyncPreparedTurn, PreparedTurn
    from ..turn import AsyncTurn, Turn


class AgentDraftSession:
    """
    A draft session enriched with the same convenience methods as :class:`AgentSession`:
    prepare_turn, list_turns, get_turn, list_events, cancel. Turn operations are delegated to a
    shared :class:`SessionMixin`, so drafts and saved sessions expose an identical turn API.
    """

    def __init__(self, session: RawDraftSession, client: TrueFoundryGateway) -> None:
        self._id: str = session.id
        self._agent_spec: AgentSpec = session.agent_spec
        self._agent_name: typing.Optional[str] = session.agent_name
        self._title: typing.Optional[str] = session.title
        self._created_by_subject: Subject = session.created_by_subject
        self._created_at: str = session.created_at
        self._updated_at: str = session.updated_at
        self._client = client
        self._mixin = SessionMixin(session.id, client)

    def __repr__(self) -> str:
        return f"AgentDraftSession(id={self._id!r}, agent_name={self._agent_name!r})"

    @property
    def type(self) -> typing.Literal["session/draft"]:
        """
        Returns
        -------
        typing.Literal["session/draft"]
            Discriminant distinguishing a draft session from a saved session.
        """
        return "session/draft"

    @property
    def id(self) -> str:
        """
        Returns
        -------
        str
            Unique identifier of this draft session.
        """
        return self._id

    @property
    def agent_spec(self) -> AgentSpec:
        """
        Returns
        -------
        AgentSpec
            Inline agent spec held by this draft.
        """
        return self._agent_spec

    @property
    def agent_name(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            Optional saved agent this draft is linked to.
        """
        return self._agent_name

    @property
    def title(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            Optional user-visible title for the draft session.
        """
        return self._title

    @property
    def created_by_subject(self) -> Subject:
        """
        Returns
        -------
        Subject
            Subject that created this draft session.
        """
        return self._created_by_subject

    @property
    def created_at(self) -> str:
        """
        Returns
        -------
        str
            ISO-8601 timestamp when the draft session was created.
        """
        return self._created_at

    @property
    def updated_at(self) -> str:
        """
        Returns
        -------
        str
            ISO-8601 timestamp when the draft session was last updated.
        """
        return self._updated_at

    def update(
        self,
        *,
        agent_spec: typing.Optional[AgentSpec] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> None:
        """
        Update this draft session's inline agent spec (owner-only). An empty call is a valid
        no-op that just refreshes ``updated_at``. Mutates ``agent_spec`` and ``updated_at`` on
        this instance in place.

        Parameters
        ----------
        agent_spec : typing.Optional[AgentSpec]
            New inline agent spec for the draft. Omit to leave the spec unchanged.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        None
        """
        response = self._client.agents.private.draft_sessions.update(
            self.id, agent_spec=agent_spec, request_options=request_options
        )
        self._agent_spec = response.data.agent_spec
        self._updated_at = response.data.updated_at

    def prepare_turn(
        self,
        *,
        input: typing.Optional[typing.Sequence[TurnInputItem]] = None,
        previous_turn_id: typing.Optional[PreviousTurnIdInput] = None,
    ) -> PreparedTurn:
        """
        Stage a turn locally; call ``execute()`` to start ``create_turn``.

        Parameters
        ----------
        input : typing.Optional[typing.Sequence[TurnInputItem]]
            Turn input items passed to create turn.
        previous_turn_id : typing.Optional[PreviousTurnIdInput]
            Previous turn to chain from. Defaults to ``auto``.

        Returns
        -------
        PreparedTurn
            Staged turn.
        """
        return self._mixin.prepare_turn(self, input=input, previous_turn_id=previous_turn_id)

    def list_turns(
        self,
        *,
        page_token: typing.Optional[str] = None,
        limit: typing.Optional[int] = 10,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SyncPager[Turn, ListTurnsResponse]:
        """
        List turns in this session.

        Parameters
        ----------
        page_token : typing.Optional[str]
            Token from the previous response ``next_page_token``.
        limit : typing.Optional[int]
            Page size. Default 10.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        SyncPager[Turn, ListTurnsResponse]
            Paginated turns.
        """
        return self._mixin.list_turns(self, page_token=page_token, limit=limit, request_options=request_options)

    def get_turn(
        self,
        turn_id: str,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> Turn:
        """
        Fetch a turn by ID.

        Parameters
        ----------
        turn_id : str
            Unique identifier of the turn to fetch.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        Turn
            Turn data.
        """
        return self._mixin.get_turn(self, turn_id, request_options=request_options)

    def cancel(self, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        """
        Cancel the running last turn for the session.

        Parameters
        ----------
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        None
        """
        self._mixin.cancel(request_options=request_options)

    def list_events(
        self,
        *,
        page_token: typing.Optional[str] = None,
        last_turn_id: typing.Optional[str] = None,
        limit: typing.Optional[int] = 100,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SyncPager[SessionEventItem, ListSessionEventsResponse]:
        """
        Paginated session events across turns (newest first); subscribe to a running turn for live events.

        Parameters
        ----------
        page_token : typing.Optional[str]
            Token from the previous response ``next_page_token``.
        last_turn_id : typing.Optional[str]
            Newest turn in the listing window (initial load only). Omit to use the session last turn.
        limit : typing.Optional[int]
            Page size. Default 100.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        SyncPager[SessionEventItem, ListSessionEventsResponse]
            Paginated session events.
        """
        return self._mixin.list_events(
            page_token=page_token,
            last_turn_id=last_turn_id,
            limit=limit,
            request_options=request_options,
        )


class AsyncAgentDraftSession:
    """
    Async version of AgentDraftSession.
    """

    def __init__(self, session: RawDraftSession, client: AsyncTrueFoundryGateway) -> None:
        self._id: str = session.id
        self._agent_spec: AgentSpec = session.agent_spec
        self._agent_name: typing.Optional[str] = session.agent_name
        self._title: typing.Optional[str] = session.title
        self._created_by_subject: Subject = session.created_by_subject
        self._created_at: str = session.created_at
        self._updated_at: str = session.updated_at
        self._client = client
        self._mixin = AsyncSessionMixin(session.id, client)

    def __repr__(self) -> str:
        return f"AsyncAgentDraftSession(id={self._id!r}, agent_name={self._agent_name!r})"

    @property
    def type(self) -> typing.Literal["session/draft"]:
        """
        Returns
        -------
        typing.Literal["session/draft"]
            Discriminant distinguishing a draft session from a saved session.
        """
        return "session/draft"

    @property
    def id(self) -> str:
        """
        Returns
        -------
        str
            Unique identifier of this draft session.
        """
        return self._id

    @property
    def agent_spec(self) -> AgentSpec:
        """
        Returns
        -------
        AgentSpec
            Inline agent spec held by this draft.
        """
        return self._agent_spec

    @property
    def agent_name(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            Optional saved agent this draft is linked to.
        """
        return self._agent_name

    @property
    def title(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            Optional user-visible title for the draft session.
        """
        return self._title

    @property
    def created_by_subject(self) -> Subject:
        """
        Returns
        -------
        Subject
            Subject that created this draft session.
        """
        return self._created_by_subject

    @property
    def created_at(self) -> str:
        """
        Returns
        -------
        str
            ISO-8601 timestamp when the draft session was created.
        """
        return self._created_at

    @property
    def updated_at(self) -> str:
        """
        Returns
        -------
        str
            ISO-8601 timestamp when the draft session was last updated.
        """
        return self._updated_at

    async def update(
        self,
        *,
        agent_spec: typing.Optional[AgentSpec] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> None:
        """
        Update this draft session's inline agent spec (owner-only). An empty call is a valid
        no-op that just refreshes ``updated_at``. Mutates ``agent_spec`` and ``updated_at`` on
        this instance in place.

        Parameters
        ----------
        agent_spec : typing.Optional[AgentSpec]
            New inline agent spec for the draft. Omit to leave the spec unchanged.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        None
        """
        response = await self._client.agents.private.draft_sessions.update(
            self.id, agent_spec=agent_spec, request_options=request_options
        )
        self._agent_spec = response.data.agent_spec
        self._updated_at = response.data.updated_at

    def prepare_turn(
        self,
        *,
        input: typing.Optional[typing.Sequence[TurnInputItem]] = None,
        previous_turn_id: typing.Optional[PreviousTurnIdInput] = None,
    ) -> AsyncPreparedTurn:
        """
        Stage a turn locally; call ``execute()`` to start ``create_turn``.

        Parameters
        ----------
        input : typing.Optional[typing.Sequence[TurnInputItem]]
            Turn input items passed to create turn.
        previous_turn_id : typing.Optional[PreviousTurnIdInput]
            Previous turn to chain from. Defaults to ``auto``.

        Returns
        -------
        AsyncPreparedTurn
            Staged turn.
        """
        return self._mixin.prepare_turn(self, input=input, previous_turn_id=previous_turn_id)

    async def list_turns(
        self,
        *,
        page_token: typing.Optional[str] = None,
        limit: typing.Optional[int] = 10,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncPager[AsyncTurn, ListTurnsResponse]:
        """
        List turns in this session.

        Parameters
        ----------
        page_token : typing.Optional[str]
            Token from the previous response ``next_page_token``.
        limit : typing.Optional[int]
            Page size. Default 10.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AsyncPager[AsyncTurn, ListTurnsResponse]
            Paginated turns.
        """
        return await self._mixin.list_turns(self, page_token=page_token, limit=limit, request_options=request_options)

    async def get_turn(
        self,
        turn_id: str,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncTurn:
        """
        Fetch a turn by ID.

        Parameters
        ----------
        turn_id : str
            Unique identifier of the turn to fetch.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AsyncTurn
            Turn data.
        """
        return await self._mixin.get_turn(self, turn_id, request_options=request_options)

    async def cancel(self, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        """
        Cancel the running last turn for the session.

        Parameters
        ----------
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        None
        """
        await self._mixin.cancel(request_options=request_options)

    async def list_events(
        self,
        *,
        page_token: typing.Optional[str] = None,
        last_turn_id: typing.Optional[str] = None,
        limit: typing.Optional[int] = 100,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncPager[SessionEventItem, ListSessionEventsResponse]:
        """
        Paginated session events across turns (newest first); subscribe to a running turn for live events.

        Parameters
        ----------
        page_token : typing.Optional[str]
            Token from the previous response ``next_page_token``.
        last_turn_id : typing.Optional[str]
            Newest turn in the listing window (initial load only). Omit to use the session last turn.
        limit : typing.Optional[int]
            Page size. Default 100.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AsyncPager[SessionEventItem, ListSessionEventsResponse]
            Paginated session events.
        """
        return await self._mixin.list_events(
            page_token=page_token,
            last_turn_id=last_turn_id,
            limit=limit,
            request_options=request_options,
        )
