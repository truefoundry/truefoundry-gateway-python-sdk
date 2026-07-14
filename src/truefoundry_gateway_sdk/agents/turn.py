from __future__ import annotations

import time
import typing

from ..types.turn_created_event import TurnCreatedEvent
from ..types.turn_done_event import TurnDoneEvent
from ..types.turn_state_cancelled import TurnStateCancelled
from ..types.turn_state_done import TurnStateDone
from ..types.turn_state_error import TurnStateError
from .turn_stream_data import TurnStreamData

if typing.TYPE_CHECKING:
    from ..client import AsyncTrueFoundryGateway, TrueFoundryGateway
    from ..core.pagination import AsyncPager, SyncPager
    from ..core.request_options import RequestOptions
    from ..types.list_events_order import ListEventsOrder
    from ..types.list_events_response import ListEventsResponse
    from ..types.subject import Subject
    from ..types.turn import Turn as RawTurn
    from ..types.turn_event import TurnEvent
    from ..types.turn_input_item import TurnInputItem
    from ..types.turn_state import TurnState
    from ..types.turn_streaming_event import TurnStreamingEvent
    from .agent_session import AsyncBaseAgentSession, BaseAgentSession

# waitForCompletion poll interval in milliseconds: default and enforced minimum.
_DEFAULT_POLL_INTERVAL_MS = 3000
_MIN_POLL_INTERVAL_MS = 3000


class Turn:
    """
    A started turn that owns all data and behavior. Identity fields are immutable;
    state is updated in-place by refresh() / wait_for_completion().
    """

    def __init__(
        self,
        turn: RawTurn,
        session: "BaseAgentSession",
        client: TrueFoundryGateway,
    ) -> None:
        self._id: str = turn.id
        self._session_id: str = turn.session_id
        self._previous_turn_id: typing.Optional[str] = turn.previous_turn_id
        self._input: typing.Optional[typing.List[TurnInputItem]] = turn.input
        self._created_by_subject: Subject = turn.created_by_subject
        self._created_at: str = turn.created_at
        self._state: TurnState = turn.state
        self._session: "BaseAgentSession" = session
        self._client = client

    def __repr__(self) -> str:
        return f"Turn(id={self._id!r}, session_id={self._session_id!r}, status={self._state.status!r})"

    @property
    def id(self) -> str:
        """
        Returns
        -------
        str
            Unique identifier of this turn.
        """
        return self._id

    @property
    def session_id(self) -> str:
        """
        Returns
        -------
        str
            Identifier of the parent session.
        """
        return self._session_id

    @property
    def previous_turn_id(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            Previous turn id in the chain, if any.
        """
        return self._previous_turn_id

    @property
    def input(self) -> typing.Optional[typing.List[TurnInputItem]]:
        """
        Returns
        -------
        typing.Optional[typing.List[TurnInputItem]]
            Input items sent when the turn was created.
        """
        return self._input

    @property
    def created_by_subject(self) -> Subject:
        """
        Returns
        -------
        Subject
            Subject that started this turn.
        """
        return self._created_by_subject

    @property
    def created_at(self) -> str:
        """
        Returns
        -------
        str
            ISO-8601 timestamp when the turn was created.
        """
        return self._created_at

    @property
    def state(self) -> TurnState:
        """
        Returns
        -------
        TurnState
            Updated by ``refresh()``, ``stream()``, and ``wait_for_completion()``.
        """
        return self._state

    @property
    def session(self) -> "BaseAgentSession":
        """
        Returns
        -------
        BaseAgentSession
            Parent session this turn belongs to.
        """
        return self._session

    def _is_terminal(self, state: TurnState) -> bool:
        # Terminal states are listed explicitly (not checking for running) so a newly added
        # non-terminal status keeps polling by default; new terminal states must be added here.
        return isinstance(state, (TurnStateDone, TurnStateCancelled, TurnStateError))

    def _apply_event(self, event: TurnStreamingEvent) -> None:
        """Keep _state in sync from streamed events that carry a state snapshot."""
        if isinstance(event, (TurnCreatedEvent, TurnDoneEvent)):
            self._state = event.state

    def refresh(self, *, request_options: typing.Optional[RequestOptions] = None) -> "Turn":
        """
        Refetch from the server, update state in-place and return self.

        Parameters
        ----------
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        Turn
            This turn with updated state.
        """
        response = self._client.agents.sessions.get_turn(self._session_id, self._id, request_options=request_options)
        self._state = response.data.state
        return self

    def wait_for_completion(
        self,
        *,
        poll_interval_ms: int = _DEFAULT_POLL_INTERVAL_MS,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> TurnState:
        """
        Poll ``get_turn`` until terminal.

        Parameters
        ----------
        poll_interval_ms : int
            Poll interval ms while waiting for completion. Minimum 3000.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        TurnState
            Terminal turn state.
        """
        if poll_interval_ms < _MIN_POLL_INTERVAL_MS:
            raise ValueError(f"poll_interval_ms must be at least {_MIN_POLL_INTERVAL_MS}ms")
        while not self._is_terminal(self._state):
            time.sleep(poll_interval_ms / 1000.0)
            self.refresh(request_options=request_options)
        return self._state

    def stream(
        self,
        *,
        after_sequence_number: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Iterator[TurnStreamData]:
        """
        Reconnect to the turn's SSE. Updates state in-place from lifecycle events.

        Parameters
        ----------
        after_sequence_number : typing.Optional[int]
            Sequence number to resume SSE subscription after.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Yields
        ------
        TurnStreamData
            SSE stream items.
        """
        for event in self._client.agents.sessions.subscribe_to_turn(
            self._session_id,
            self._id,
            after_sequence_number=after_sequence_number,
            request_options=request_options,
        ):
            self._apply_event(event)
            yield TurnStreamData(sequence_number=None, event=event)

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
        self._client.agents.sessions.cancel(self._session_id, request_options=request_options)

    def list_events(
        self,
        *,
        page_token: typing.Optional[str] = None,
        limit: typing.Optional[int] = 25,
        order: typing.Optional[ListEventsOrder] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SyncPager[TurnEvent, ListEventsResponse]:
        """
        Paginated persisted events; use ``stream()`` for live SSE.

        Parameters
        ----------
        page_token : typing.Optional[str]
            Token from the previous response ``next_page_token``.
        limit : typing.Optional[int]
            Page size. Default 25.
        order : typing.Optional[ListEventsOrder]
            Sort by creation time. Default ``asc``.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        SyncPager[TurnEvent, ListEventsResponse]
            Paginated turn events.
        """
        return self._client.agents.sessions.list_turn_events(
            self._session_id,
            self._id,
            page_token=page_token,
            limit=limit,
            order=order,
            request_options=request_options,
        )


class AsyncTurn:
    """
    Async version of Turn. Same interface with async methods.
    """

    def __init__(
        self,
        turn: RawTurn,
        session: "AsyncBaseAgentSession",
        client: AsyncTrueFoundryGateway,
    ) -> None:
        self._id: str = turn.id
        self._session_id: str = turn.session_id
        self._previous_turn_id: typing.Optional[str] = turn.previous_turn_id
        self._input: typing.Optional[typing.List[TurnInputItem]] = turn.input
        self._created_by_subject: Subject = turn.created_by_subject
        self._created_at: str = turn.created_at
        self._state: TurnState = turn.state
        self._session: "AsyncBaseAgentSession" = session
        self._client: AsyncTrueFoundryGateway = client

    def __repr__(self) -> str:
        return f"AsyncTurn(id={self._id!r}, session_id={self._session_id!r}, status={self._state.status!r})"

    @property
    def id(self) -> str:
        """
        Returns
        -------
        str
            Unique identifier of this turn.
        """
        return self._id

    @property
    def session_id(self) -> str:
        """
        Returns
        -------
        str
            Identifier of the parent session.
        """
        return self._session_id

    @property
    def previous_turn_id(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            Previous turn id in the chain, if any.
        """
        return self._previous_turn_id

    @property
    def input(self) -> typing.Optional[typing.List[TurnInputItem]]:
        """
        Returns
        -------
        typing.Optional[typing.List[TurnInputItem]]
            Input items sent when the turn was created.
        """
        return self._input

    @property
    def created_by_subject(self) -> Subject:
        """
        Returns
        -------
        Subject
            Subject that started this turn.
        """
        return self._created_by_subject

    @property
    def created_at(self) -> str:
        """
        Returns
        -------
        str
            ISO-8601 timestamp when the turn was created.
        """
        return self._created_at

    @property
    def state(self) -> TurnState:
        """
        Returns
        -------
        TurnState
            Updated by ``refresh()``, ``stream()``, and ``wait_for_completion()``.
        """
        return self._state

    @property
    def session(self) -> "AsyncBaseAgentSession":
        """
        Returns
        -------
        AsyncBaseAgentSession
            Parent session this turn belongs to.
        """
        return self._session

    def _is_terminal(self, state: TurnState) -> bool:
        # Terminal states are listed explicitly (not checking for running) so a newly added
        # non-terminal status keeps polling by default; new terminal states must be added here.
        return isinstance(state, (TurnStateDone, TurnStateCancelled, TurnStateError))

    def _apply_event(self, event: TurnStreamingEvent) -> None:
        """Keep _state in sync from streamed events that carry a state snapshot."""
        if isinstance(event, (TurnCreatedEvent, TurnDoneEvent)):
            self._state = event.state

    async def refresh(self, *, request_options: typing.Optional[RequestOptions] = None) -> "AsyncTurn":
        """
        Refetch from the server, update state in-place and return self.

        Parameters
        ----------
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AsyncTurn
            This turn with updated state.
        """
        response = await self._client.agents.sessions.get_turn(
            self._session_id, self._id, request_options=request_options
        )
        self._state = response.data.state
        return self

    async def wait_for_completion(
        self,
        *,
        poll_interval_ms: int = _DEFAULT_POLL_INTERVAL_MS,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> TurnState:
        """
        Poll ``get_turn`` until terminal.

        Parameters
        ----------
        poll_interval_ms : int
            Poll interval ms while waiting for completion. Minimum 3000.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        TurnState
            Terminal turn state.
        """
        import asyncio

        if poll_interval_ms < _MIN_POLL_INTERVAL_MS:
            raise ValueError(f"poll_interval_ms must be at least {_MIN_POLL_INTERVAL_MS}ms")
        while not self._is_terminal(self._state):
            await asyncio.sleep(poll_interval_ms / 1000.0)
            await self.refresh(request_options=request_options)
        return self._state

    async def stream(
        self,
        *,
        after_sequence_number: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.AsyncIterator[TurnStreamData]:
        """
        Reconnect to the turn's SSE. Updates state in-place from lifecycle events.

        Parameters
        ----------
        after_sequence_number : typing.Optional[int]
            Sequence number to resume SSE subscription after.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Yields
        ------
        TurnStreamData
            SSE stream items.
        """
        async for event in self._client.agents.sessions.subscribe_to_turn(
            self._session_id,
            self._id,
            after_sequence_number=after_sequence_number,
            request_options=request_options,
        ):
            self._apply_event(event)
            yield TurnStreamData(sequence_number=None, event=event)

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
        await self._client.agents.sessions.cancel(self._session_id, request_options=request_options)

    async def list_events(
        self,
        *,
        page_token: typing.Optional[str] = None,
        limit: typing.Optional[int] = 25,
        order: typing.Optional[ListEventsOrder] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncPager[TurnEvent, ListEventsResponse]:
        """
        Paginated persisted events; use ``stream()`` for live SSE.

        Parameters
        ----------
        page_token : typing.Optional[str]
            Token from the previous response ``next_page_token``.
        limit : typing.Optional[int]
            Page size. Default 25.
        order : typing.Optional[ListEventsOrder]
            Sort by creation time. Default ``asc``.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AsyncPager[TurnEvent, ListEventsResponse]
            Paginated turn events.
        """
        return await self._client.agents.sessions.list_turn_events(
            self._session_id,
            self._id,
            page_token=page_token,
            limit=limit,
            order=order,
            request_options=request_options,
        )
