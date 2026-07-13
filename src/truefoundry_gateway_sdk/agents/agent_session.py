from __future__ import annotations

import typing

from ..core.pagination import AsyncPager, SyncPager
from .prepared_turn import AsyncPreparedTurn, PreparedTurn
from .turn import AsyncTurn, Turn

if typing.TYPE_CHECKING:
    from ..client import AsyncTrueFoundryGateway, TrueFoundryGateway
    from ..core.request_options import RequestOptions
    from ..types.list_session_events_response import ListSessionEventsResponse
    from ..types.list_turns_response import ListTurnsResponse
    from ..types.previous_turn_id_input import PreviousTurnIdInput
    from ..types.session import Session as RawSession
    from ..types.session_event_item import SessionEventItem
    from ..types.subject import Subject
    from ..types.turn import Turn as RawTurn
    from ..types.turn_input_item import TurnInputItem


def _wrap_turns_pager(
    raw_pager: SyncPager[RawTurn, ListTurnsResponse],
    session: "AgentSession",
    client: TrueFoundryGateway,
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
    client: AsyncTrueFoundryGateway,
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
    A session enriched with convenience methods: prepare_turn, list_turns, get_turn, list_events, cancel.
    """

    def __init__(self, session: RawSession, client: TrueFoundryGateway) -> None:
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
        """
        Returns
        -------
        str
            Unique identifier of this session.
        """
        return self._id

    @property
    def agent_name(self) -> str:
        """
        Returns
        -------
        str
            Name of the agent for this session.
        """
        return self._agent_name

    @property
    def title(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            Optional user-visible title for the session.
        """
        return self._title

    @property
    def created_by_subject(self) -> Subject:
        """
        Returns
        -------
        Subject
            Subject that created this session.
        """
        return self._created_by_subject

    @property
    def created_at(self) -> str:
        """
        Returns
        -------
        str
            ISO-8601 timestamp when the session was created.
        """
        return self._created_at

    @property
    def updated_at(self) -> str:
        """
        Returns
        -------
        str
            ISO-8601 timestamp when the session was last updated.
        """
        return self._updated_at

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
        response = self._client.agents.sessions.get_turn(self._id, turn_id, request_options=request_options)
        return Turn(response.data, self, self._client)

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
        self._client.agents.sessions.cancel(self._id, request_options=request_options)

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
        return self._client.agents.sessions.list_events(
            self._id,
            page_token=page_token,
            last_turn_id=last_turn_id,
            limit=limit,
            request_options=request_options,
        )


class AsyncAgentSession:
    """
    Async version of AgentSession.
    """

    def __init__(self, session: RawSession, client: AsyncTrueFoundryGateway) -> None:
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
        """
        Returns
        -------
        str
            Unique identifier of this session.
        """
        return self._id

    @property
    def agent_name(self) -> str:
        """
        Returns
        -------
        str
            Name of the agent for this session.
        """
        return self._agent_name

    @property
    def title(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            Optional user-visible title for the session.
        """
        return self._title

    @property
    def created_by_subject(self) -> Subject:
        """
        Returns
        -------
        Subject
            Subject that created this session.
        """
        return self._created_by_subject

    @property
    def created_at(self) -> str:
        """
        Returns
        -------
        str
            ISO-8601 timestamp when the session was created.
        """
        return self._created_at

    @property
    def updated_at(self) -> str:
        """
        Returns
        -------
        str
            ISO-8601 timestamp when the session was last updated.
        """
        return self._updated_at

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
        response = await self._client.agents.sessions.get_turn(self._id, turn_id, request_options=request_options)
        return AsyncTurn(response.data, self, self._client)

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
        await self._client.agents.sessions.cancel(self._id, request_options=request_options)

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
        return await self._client.agents.sessions.list_events(
            self._id,
            page_token=page_token,
            last_turn_id=last_turn_id,
            limit=limit,
            request_options=request_options,
        )
