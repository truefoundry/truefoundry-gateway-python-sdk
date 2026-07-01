import typing

from ..core.pagination import AsyncPager, SyncPager
from ..core.request_options import RequestOptions
from ..types.list_events_order import ListEventsOrder
from ..types.list_events_response import ListEventsResponse
from ..types.previous_turn_id_input import PreviousTurnIdInput
from ..types.subject import Subject
from ..types.turn import Turn as RawTurn
from ..types.turn_created_event import TurnCreatedEvent
from ..types.turn_done_event import TurnDoneEvent
from ..types.turn_event import TurnEvent
from ..types.turn_input_item import TurnInputItem
from ..types.turn_state import TurnState
from .turn import AsyncTurn, Turn
from .turn_stream_data import TurnStreamData

if typing.TYPE_CHECKING:
    from .agent_session import AgentSession, AsyncAgentSession


class PreparedTurn:
    """
    Output of prepare_turn: not yet started (no HTTP). execute() fires the create_turn POST
    and drives the SSE stream. The inner Turn is adopted once turn.created is received.
    """

    def __init__(
        self,
        *,
        input: typing.Optional[typing.Sequence[TurnInputItem]],
        previous_turn_id: typing.Optional[PreviousTurnIdInput],
        session: "AgentSession",
        client: typing.Any,
    ) -> None:
        self._input = list(input) if input is not None else None
        self._previous_turn_id = previous_turn_id
        self._session: "AgentSession" = session
        self._session_id: str = session.id
        self._client = client
        self._started: bool = False
        self._turn: typing.Optional[Turn] = None

    def __repr__(self) -> str:
        return f"PreparedTurn(session_id={self._session_id!r}, started={self._started!r})"

    # --- Properties that delegate to the inner Turn (None until execute is called) ---

    @property
    def session(self) -> "AgentSession":
        return self._session

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def id(self) -> typing.Optional[str]:
        """None until ``execute()`` has started the turn."""
        return self._turn.id if self._turn is not None else None

    @property
    def previous_turn_id(self) -> typing.Optional[str]:
        return self._turn.previous_turn_id if self._turn is not None else None

    @property
    def state(self) -> typing.Optional[TurnState]:
        return self._turn.state if self._turn is not None else None

    @property
    def created_by_subject(self) -> typing.Optional[Subject]:
        return self._turn.created_by_subject if self._turn is not None else None

    @property
    def created_at(self) -> typing.Optional[str]:
        return self._turn.created_at if self._turn is not None else None

    @property
    def input(self) -> typing.Optional[typing.List[TurnInputItem]]:
        if self._turn is not None:
            return self._turn.input
        return self._input  # type: ignore[return-value]

    # --- Execute: the ONLY initiator ---

    @typing.overload
    def execute(
        self,
        *,
        stream: typing.Literal[False],
        poll_interval_ms: int = ...,
        request_options: typing.Optional[RequestOptions] = ...,
    ) -> TurnState: ...

    @typing.overload
    def execute(
        self,
        *,
        stream: typing.Literal[True] = ...,
        request_options: typing.Optional[RequestOptions] = ...,
    ) -> typing.Iterator[TurnStreamData]: ...

    def execute(
        self,
        *,
        stream: bool = True,
        poll_interval_ms: int = 3000,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Union[typing.Iterator[TurnStreamData], TurnState]:
        """Start the turn via create_turn. ``stream=True`` (default) yields SSE from that POST (not resumable; after disconnect call ``stream()`` to subscribe_to_turn). ``stream=False`` polls ``get_turn`` until done, cancelled, or error."""
        if self._started:
            raise RuntimeError("Turn already started; use stream() / wait_for_completion().")
        self._started = True
        if stream:
            return self._run_streaming(request_options)
        else:
            return self._start_and_wait(poll_interval_ms, request_options)

    # --- Post-execution delegating behaviors ---

    def stream(
        self,
        *,
        after_sequence_number: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Iterator[TurnStreamData]:
        """Subscribe to live SSE via subscribe_to_turn after ``execute()`` has started the turn. Pass ``after_sequence_number`` to resume; updates state from turn.created and turn.done."""
        yield from self._must_get_turn().stream(
            after_sequence_number=after_sequence_number, request_options=request_options
        )

    def refresh(self, *, request_options: typing.Optional[RequestOptions] = None) -> "PreparedTurn":
        """Refetch from the server, update state in-place and return self."""
        self._must_get_turn().refresh(request_options=request_options)
        return self

    def wait_for_completion(
        self,
        *,
        poll_interval_ms: int = 3000,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> TurnState:
        """Poll ``get_turn`` until the turn is done, cancelled, or errored. ``poll_interval_ms`` minimum is 3000."""
        return self._must_get_turn().wait_for_completion(
            poll_interval_ms=poll_interval_ms, request_options=request_options
        )

    def cancel(self, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        """Cancel the running last turn for the session."""
        return self._must_get_turn().cancel(request_options=request_options)

    def list_events(
        self,
        *,
        page_token: typing.Optional[str] = None,
        limit: typing.Optional[int] = 25,
        order: typing.Optional[ListEventsOrder] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SyncPager[TurnEvent, ListEventsResponse]:
        """Paginated persisted TurnEvent history (no streaming deltas). Use ``stream()`` for live TurnStreamingEvent SSE."""
        return self._must_get_turn().list_events(
            page_token=page_token, limit=limit, order=order, request_options=request_options
        )

    # --- Private helpers ---

    def _run_streaming(self, request_options: typing.Optional[RequestOptions]) -> typing.Iterator[TurnStreamData]:
        """execute(stream=True) path: open create_turn SSE, adopt inner Turn on turn.created."""
        yield from self._consume_stream(request_options)

    def _start_and_wait(self, poll_interval_ms: int, request_options: typing.Optional[RequestOptions]) -> TurnState:
        """execute(stream=False) path: drive SSE until turn.created mints the inner Turn, then poll."""
        self._create_turn_if_not_exist(request_options)
        return self._must_get_turn().wait_for_completion(
            poll_interval_ms=poll_interval_ms, request_options=request_options
        )

    def _consume_stream(self, request_options: typing.Optional[RequestOptions]) -> typing.Iterator[TurnStreamData]:
        """Consume the create_turn SSE, adopting the inner Turn from the first turn.created."""
        for event in self._client.agents.sessions.create_turn(
            self._session_id,
            input=self._input,
            previous_turn_id=self._previous_turn_id,
            request_options=request_options,
        ):
            if isinstance(event, TurnCreatedEvent) and self._turn is None:
                self._adopt_turn(event)
            elif self._turn is not None and isinstance(event, TurnDoneEvent):
                self._replace_turn_state(event.state)
            yield TurnStreamData(sequence_number=None, event=event)

    def _must_get_turn(self) -> Turn:
        if self._turn is None:
            raise RuntimeError("Turn not started yet; call execute() first.")
        return self._turn

    def _create_turn_if_not_exist(self, request_options: typing.Optional[RequestOptions]) -> None:
        """Drive the create_turn SSE only until the first turn.created builds the inner Turn, then stop."""
        if self._turn is None:
            for _ in self._consume_stream(request_options):
                if self._turn is not None:
                    break

    def _adopt_turn(self, event: TurnCreatedEvent) -> None:
        """Build the inner Turn directly from the turn.created event."""
        self._turn = Turn(
            RawTurn(
                id=event.turn_id,
                session_id=self._session_id,
                previous_turn_id=event.previous_turn_id,
                input=self._input,  # type: ignore[arg-type]
                state=event.state,
                created_by_subject=event.created_by,
                created_at=event.created_at,
            ),
            self._session,
            self._client,
        )

    def _replace_turn_state(self, state: TurnState) -> None:
        """Replace the inner Turn with a fresh one carrying the new state."""
        turn = self._must_get_turn()
        self._turn = Turn(
            RawTurn(
                id=turn.id,
                session_id=turn.session_id,
                previous_turn_id=turn.previous_turn_id,
                input=turn.input,  # type: ignore[arg-type]
                state=state,
                created_by_subject=turn.created_by_subject,
                created_at=turn.created_at,
            ),
            self._session,
            self._client,
        )


class AsyncPreparedTurn:
    """
    Async version of PreparedTurn.
    """

    def __init__(
        self,
        *,
        input: typing.Optional[typing.Sequence[TurnInputItem]],
        previous_turn_id: typing.Optional[PreviousTurnIdInput],
        session: "AsyncAgentSession",
        client: typing.Any,
    ) -> None:
        self._input = list(input) if input is not None else None
        self._previous_turn_id = previous_turn_id
        self._session: "AsyncAgentSession" = session
        self._session_id: str = session.id
        self._client = client
        self._started: bool = False
        self._turn: typing.Optional[AsyncTurn] = None

    def __repr__(self) -> str:
        return f"AsyncPreparedTurn(session_id={self._session_id!r}, started={self._started!r})"

    # --- Properties that delegate to the inner AsyncTurn (None until execute is called) ---

    @property
    def session(self) -> "AsyncAgentSession":
        return self._session

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def id(self) -> typing.Optional[str]:
        """None until ``execute()`` has started the turn."""
        return self._turn.id if self._turn is not None else None

    @property
    def previous_turn_id(self) -> typing.Optional[str]:
        return self._turn.previous_turn_id if self._turn is not None else None

    @property
    def state(self) -> typing.Optional[TurnState]:
        return self._turn.state if self._turn is not None else None

    @property
    def created_by_subject(self) -> typing.Optional[Subject]:
        return self._turn.created_by_subject if self._turn is not None else None

    @property
    def created_at(self) -> typing.Optional[str]:
        return self._turn.created_at if self._turn is not None else None

    @property
    def input(self) -> typing.Optional[typing.List[TurnInputItem]]:
        if self._turn is not None:
            return self._turn.input
        return self._input  # type: ignore[return-value]

    # --- Execute: the ONLY initiator ---

    @typing.overload
    async def execute(
        self,
        *,
        stream: typing.Literal[False],
        poll_interval_ms: int = ...,
        request_options: typing.Optional[RequestOptions] = ...,
    ) -> TurnState: ...

    @typing.overload
    def execute(
        self,
        *,
        stream: typing.Literal[True] = ...,
        request_options: typing.Optional[RequestOptions] = ...,
    ) -> typing.AsyncIterator[TurnStreamData]: ...

    def execute(
        self,
        *,
        stream: bool = True,
        poll_interval_ms: int = 3000,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Union[typing.AsyncIterator[TurnStreamData], "typing.Coroutine[typing.Any, typing.Any, TurnState]"]:
        """Start the turn via create_turn. ``stream=True`` (default) yields SSE from that POST (not resumable; after disconnect call ``stream()`` to subscribe_to_turn). ``stream=False`` polls ``get_turn`` until done, cancelled, or error."""
        if self._started:
            raise RuntimeError("Turn already started; use stream() / wait_for_completion().")
        self._started = True
        if stream:
            return self._run_streaming(request_options)
        else:
            return self._start_and_wait(poll_interval_ms, request_options)

    # --- Post-execution delegating behaviors ---

    async def stream(
        self,
        *,
        after_sequence_number: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.AsyncIterator[TurnStreamData]:
        """Subscribe to live SSE via subscribe_to_turn after ``execute()`` has started the turn. Pass ``after_sequence_number`` to resume; updates state from turn.created and turn.done."""
        async for item in self._must_get_turn().stream(
            after_sequence_number=after_sequence_number, request_options=request_options
        ):
            yield item

    async def refresh(self, *, request_options: typing.Optional[RequestOptions] = None) -> "AsyncPreparedTurn":
        """Refetch from the server, update state in-place and return self."""
        await self._must_get_turn().refresh(request_options=request_options)
        return self

    async def wait_for_completion(
        self,
        *,
        poll_interval_ms: int = 3000,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> TurnState:
        """Poll ``get_turn`` until the turn is done, cancelled, or errored. ``poll_interval_ms`` minimum is 3000."""
        return await self._must_get_turn().wait_for_completion(
            poll_interval_ms=poll_interval_ms, request_options=request_options
        )

    async def cancel(self, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        """Cancel the running last turn for the session."""
        return await self._must_get_turn().cancel(request_options=request_options)

    async def list_events(
        self,
        *,
        page_token: typing.Optional[str] = None,
        limit: typing.Optional[int] = 25,
        order: typing.Optional[ListEventsOrder] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncPager[TurnEvent, ListEventsResponse]:
        """Paginated persisted TurnEvent history (no streaming deltas). Use ``stream()`` for live TurnStreamingEvent SSE."""
        return await self._must_get_turn().list_events(
            page_token=page_token, limit=limit, order=order, request_options=request_options
        )

    # --- Private helpers ---

    async def _run_streaming(
        self, request_options: typing.Optional[RequestOptions]
    ) -> typing.AsyncIterator[TurnStreamData]:
        async for item in self._consume_stream(request_options):
            yield item

    async def _start_and_wait(
        self, poll_interval_ms: int, request_options: typing.Optional[RequestOptions]
    ) -> TurnState:
        await self._create_turn_if_not_exist(request_options)
        return await self._must_get_turn().wait_for_completion(
            poll_interval_ms=poll_interval_ms, request_options=request_options
        )

    async def _consume_stream(
        self, request_options: typing.Optional[RequestOptions]
    ) -> typing.AsyncIterator[TurnStreamData]:
        async for event in self._client.agents.sessions.create_turn(
            self._session_id,
            input=self._input,
            previous_turn_id=self._previous_turn_id,
            request_options=request_options,
        ):
            if isinstance(event, TurnCreatedEvent) and self._turn is None:
                self._adopt_turn(event)
            elif self._turn is not None and isinstance(event, TurnDoneEvent):
                self._replace_turn_state(event.state)
            yield TurnStreamData(sequence_number=None, event=event)

    def _must_get_turn(self) -> AsyncTurn:
        if self._turn is None:
            raise RuntimeError("Turn not started yet; call execute() first.")
        return self._turn

    async def _create_turn_if_not_exist(self, request_options: typing.Optional[RequestOptions]) -> None:
        if self._turn is None:
            async for _ in self._consume_stream(request_options):
                if self._turn is not None:
                    break

    def _adopt_turn(self, event: TurnCreatedEvent) -> None:
        self._turn = AsyncTurn(
            RawTurn(
                id=event.turn_id,
                session_id=self._session_id,
                previous_turn_id=event.previous_turn_id,
                input=self._input,  # type: ignore[arg-type]
                state=event.state,
                created_by_subject=event.created_by,
                created_at=event.created_at,
            ),
            self._session,
            self._client,
        )

    def _replace_turn_state(self, state: TurnState) -> None:
        """Replace the inner Turn with a fresh one carrying the new state."""
        turn = self._must_get_turn()
        self._turn = AsyncTurn(
            RawTurn(
                id=turn.id,
                session_id=turn.session_id,
                previous_turn_id=turn.previous_turn_id,
                input=turn.input,  # type: ignore[arg-type]
                state=state,
                created_by_subject=turn.created_by_subject,
                created_at=turn.created_at,
            ),
            self._session,
            self._client,
        )
