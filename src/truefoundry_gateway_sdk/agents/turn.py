import time
import typing

from ..core.pagination import AsyncPager, SyncPager
from ..core.request_options import RequestOptions
from ..types.list_events_order import ListEventsOrder
from ..types.list_events_response import ListEventsResponse
from ..types.subject import Subject
from ..types.turn import Turn as RawTurn
from ..types.turn_created_event import TurnCreatedEvent
from ..types.turn_done_event import TurnDoneEvent
from ..types.turn_event import TurnEvent
from ..types.turn_input_item import TurnInputItem
from ..types.turn_state import TurnState
from ..types.turn_state_cancelled import TurnStateCancelled
from ..types.turn_state_done import TurnStateDone
from ..types.turn_state_error import TurnStateError
from ..types.turn_streaming_event import TurnStreamingEvent
from .turn_stream_data import TurnStreamData

if typing.TYPE_CHECKING:
    from .agent_session import AgentSession, AsyncAgentSession

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
        session: "AgentSession",
        client: typing.Any,
    ) -> None:
        from ..client import TrueFoundryGateway

        self._id: str = turn.id
        self._session_id: str = turn.session_id
        self._previous_turn_id: typing.Optional[str] = turn.previous_turn_id
        self._input: typing.Optional[typing.List[TurnInputItem]] = turn.input
        self._created_by_subject: Subject = turn.created_by_subject
        self._created_at: str = turn.created_at
        self._state: TurnState = turn.state
        self._session: "AgentSession" = session
        self._client: TrueFoundryGateway = client

    def __repr__(self) -> str:
        return f"Turn(id={self._id!r}, session_id={self._session_id!r}, status={self._state.status!r})"

    @property
    def id(self) -> str:
        return self._id

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def previous_turn_id(self) -> typing.Optional[str]:
        return self._previous_turn_id

    @property
    def input(self) -> typing.Optional[typing.List[TurnInputItem]]:
        return self._input

    @property
    def created_by_subject(self) -> Subject:
        return self._created_by_subject

    @property
    def created_at(self) -> str:
        return self._created_at

    @property
    def state(self) -> TurnState:
        return self._state

    @property
    def session(self) -> "AgentSession":
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
        """Refetch from the server, update state in-place and return self."""
        response = self._client.agents.sessions.get_turn(self._session_id, self._id, request_options=request_options)
        self._state = response.data.state
        return self

    def wait_for_completion(
        self,
        *,
        poll_interval_ms: int = _DEFAULT_POLL_INTERVAL_MS,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> TurnState:
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
        """Reconnect to the turn's SSE. Updates state in-place from lifecycle events."""
        for event in self._client.agents.sessions.subscribe_to_turn(
            self._session_id,
            self._id,
            after_sequence_number=after_sequence_number,
            request_options=request_options,
        ):
            self._apply_event(event)
            yield TurnStreamData(sequence_number=None, event=event)

    def cancel(self, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        self._client.agents.sessions.cancel(self._session_id, request_options=request_options)

    def list_events(
        self,
        *,
        page_token: typing.Optional[str] = None,
        limit: typing.Optional[int] = 25,
        order: typing.Optional[ListEventsOrder] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SyncPager[TurnEvent, ListEventsResponse]:
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
        session: "AsyncAgentSession",
        client: typing.Any,
    ) -> None:
        from ..client import AsyncTrueFoundryGateway

        self._id: str = turn.id
        self._session_id: str = turn.session_id
        self._previous_turn_id: typing.Optional[str] = turn.previous_turn_id
        self._input: typing.Optional[typing.List[TurnInputItem]] = turn.input
        self._created_by_subject: Subject = turn.created_by_subject
        self._created_at: str = turn.created_at
        self._state: TurnState = turn.state
        self._session: "AsyncAgentSession" = session
        self._client: AsyncTrueFoundryGateway = client

    def __repr__(self) -> str:
        return f"AsyncTurn(id={self._id!r}, session_id={self._session_id!r}, status={self._state.status!r})"

    @property
    def id(self) -> str:
        return self._id

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def previous_turn_id(self) -> typing.Optional[str]:
        return self._previous_turn_id

    @property
    def input(self) -> typing.Optional[typing.List[TurnInputItem]]:
        return self._input

    @property
    def created_by_subject(self) -> Subject:
        return self._created_by_subject

    @property
    def created_at(self) -> str:
        return self._created_at

    @property
    def state(self) -> TurnState:
        return self._state

    @property
    def session(self) -> "AsyncAgentSession":
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
        """Refetch from the server, update state in-place and return self."""
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
        """Reconnect to the turn's SSE. Updates state in-place from lifecycle events."""
        async for event in self._client.agents.sessions.subscribe_to_turn(
            self._session_id,
            self._id,
            after_sequence_number=after_sequence_number,
            request_options=request_options,
        ):
            self._apply_event(event)
            yield TurnStreamData(sequence_number=None, event=event)

    async def cancel(self, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        await self._client.agents.sessions.cancel(self._session_id, request_options=request_options)

    async def list_events(
        self,
        *,
        page_token: typing.Optional[str] = None,
        limit: typing.Optional[int] = 25,
        order: typing.Optional[ListEventsOrder] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncPager[TurnEvent, ListEventsResponse]:
        return await self._client.agents.sessions.list_turn_events(
            self._session_id,
            self._id,
            page_token=page_token,
            limit=limit,
            order=order,
            request_options=request_options,
        )
