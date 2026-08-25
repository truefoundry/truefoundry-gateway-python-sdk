from __future__ import annotations

import typing

from ..types.turn import Turn as RawTurn
from ..types.turn_created_event import TurnCreatedEvent
from ..types.turn_done_event import TurnDoneEvent
from .turn import AsyncTurn, Turn
from .turn_stream_data import TurnStreamData, parse_sequence_number

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)

if typing.TYPE_CHECKING:
    from ..client import AsyncTrueFoundryGateway, TrueFoundryGateway
    from ..core.pagination import AsyncPager, SyncPager
    from ..core.request_options import RequestOptions
    from ..types.list_events_order import ListEventsOrder
    from ..types.list_events_response import ListEventsResponse
    from ..types.previous_turn_id_input import PreviousTurnIdInput
    from ..types.subject import Subject
    from ..types.turn_event import TurnEvent
    from ..types.turn_input_item import TurnInputItem
    from ..types.turn_state import TurnState
    from .agent_session import AgentSession, AsyncAgentSession
    from .private.agent_draft_session import AgentDraftSession, AsyncAgentDraftSession


class PreparedTurn:
    """
    Output of prepare_turn: not yet started (no HTTP). execute() starts the turn via
    create_turn_stream (SSE) or create_turn (JSON), then drives the inner Turn.
    """

    def __init__(
        self,
        *,
        input: typing.Optional[typing.Sequence[TurnInputItem]],
        previous_turn_id: typing.Optional[PreviousTurnIdInput],
        session: typing.Union["AgentSession", "AgentDraftSession"],
        client: TrueFoundryGateway,
    ) -> None:
        # Keep the raw value (which may be the OMIT sentinel) to forward to create_turn
        # unchanged; self._input is the list-or-None form used for local state/exposure.
        self._input_param = input
        self._input = list(input) if input is not None and input is not OMIT else None
        self._previous_turn_id = previous_turn_id
        self._session: typing.Union["AgentSession", "AgentDraftSession"] = session
        self._session_id: str = session.id
        self._client = client
        self._started: bool = False
        self._turn: typing.Optional[Turn] = None

    def __repr__(self) -> str:
        return f"PreparedTurn(session_id={self._session_id!r}, started={self._started!r})"

    # --- Properties that delegate to the inner Turn (None until execute is called) ---

    @property
    def session(self) -> typing.Union["AgentSession", "AgentDraftSession"]:
        """
        Returns
        -------
        typing.Union[AgentSession, AgentDraftSession]
            Parent session this prepared turn belongs to.
        """
        return self._session

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
    def id(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            None until ``execute()`` starts the turn.
        """
        return self._turn.id if self._turn is not None else None

    @property
    def previous_turn_id(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            None until ``execute()`` starts the turn.
        """
        return self._turn.previous_turn_id if self._turn is not None else None

    @property
    def state(self) -> typing.Optional[TurnState]:
        """
        Returns
        -------
        typing.Optional[TurnState]
            None until ``execute()`` starts the turn.
        """
        return self._turn.state if self._turn is not None else None

    @property
    def created_by_subject(self) -> typing.Optional[Subject]:
        """
        Returns
        -------
        typing.Optional[Subject]
            None until ``execute()`` starts the turn.
        """
        return self._turn.created_by_subject if self._turn is not None else None

    @property
    def created_at(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            None until ``execute()`` starts the turn.
        """
        return self._turn.created_at if self._turn is not None else None

    @property
    def input(self) -> typing.Optional[typing.List[TurnInputItem]]:
        """
        Returns
        -------
        typing.Optional[typing.List[TurnInputItem]]
            Staged input before ``execute()``; inner turn input after.
        """
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
        """
        Start the turn via ``create_turn_stream`` / ``create_turn``.

        Parameters
        ----------
        stream : bool
            Stream ``create_turn_stream`` SSE when true. Default true.
            When false, uses ``create_turn`` JSON then polls to terminal.
        poll_interval_ms : int
            Poll interval ms when ``stream=False``. Minimum 3000.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        TurnState
            Terminal turn state.

        Yields
        ------
        TurnStreamData
            SSE stream from create_turn_stream.
        """
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
        after_sequence_number: typing.Optional[int] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Iterator[TurnStreamData]:
        """
        Resubscribe via ``subscribe_to_turn`` after ``execute()``.

        Parameters
        ----------
        after_sequence_number : typing.Optional[int]
            Sequence number to resume SSE subscription after. Omit to resume via the
            Last-Event-Id header instead.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Yields
        ------
        TurnStreamData
            SSE stream items.
        """
        yield from self._must_get_turn().stream(
            after_sequence_number=after_sequence_number, request_options=request_options
        )

    def refresh(self, *, request_options: typing.Optional[RequestOptions] = None) -> "PreparedTurn":
        """
        Refetch from the server, update state in-place and return self.

        Parameters
        ----------
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        PreparedTurn
            This prepared turn with updated state.
        """
        self._must_get_turn().refresh(request_options=request_options)
        return self

    def wait_for_completion(
        self,
        *,
        poll_interval_ms: int = 3000,
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
        return self._must_get_turn().wait_for_completion(
            poll_interval_ms=poll_interval_ms, request_options=request_options
        )

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
        return self._must_get_turn().cancel(request_options=request_options)

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
        return self._must_get_turn().list_events(
            page_token=page_token, limit=limit, order=order, request_options=request_options
        )

    # --- Private helpers ---

    def _run_streaming(self, request_options: typing.Optional[RequestOptions]) -> typing.Iterator[TurnStreamData]:
        """execute(stream=True) path: open create_turn_stream SSE, adopt inner Turn on turn.created."""
        yield from self._consume_stream(request_options)

    def _start_and_wait(self, poll_interval_ms: int, request_options: typing.Optional[RequestOptions]) -> TurnState:
        """execute(stream=False) path: create_turn JSON returns the running turn; then poll."""
        response = self._client.agents.sessions.create_turn(
            self._session_id,
            input=self._input_param,
            previous_turn_id=self._previous_turn_id,
            request_options=request_options,
        )
        self._adopt_turn_from_api(response.data)
        return self._must_get_turn().wait_for_completion(
            poll_interval_ms=poll_interval_ms, request_options=request_options
        )

    def _consume_stream(self, request_options: typing.Optional[RequestOptions]) -> typing.Iterator[TurnStreamData]:
        """Consume create_turn_stream SSE, adopting the inner Turn from the first turn.created."""
        with self._client.agents.sessions.create_turn_stream(
            self._session_id,
            input=self._input_param,
            previous_turn_id=self._previous_turn_id,
            request_options=request_options,
        ) as sse:
            for event in sse.with_metadata():
                sequence_number = parse_sequence_number(event.id)
                if isinstance(event.data, TurnCreatedEvent) and self._turn is None:
                    self._adopt_turn_from_created_event(event.data)
                elif self._turn is not None and isinstance(event.data, TurnDoneEvent):
                    self._replace_turn_state(event.data.state)
                yield TurnStreamData(sequence_number=sequence_number, event=event.data)

    def _must_get_turn(self) -> Turn:
        if self._turn is None:
            raise RuntimeError("Turn not started yet; call execute() first.")
        return self._turn

    def _adopt_turn_from_api(self, turn: RawTurn) -> None:
        """Build the inner Turn from create_turn / get_turn response data."""
        self._turn = Turn(
            RawTurn(
                id=turn.id,
                session_id=turn.session_id,
                previous_turn_id=turn.previous_turn_id,
                input=turn.input if turn.input is not None else self._input,  # type: ignore[arg-type]
                state=turn.state,
                created_by_subject=turn.created_by_subject,
                created_at=turn.created_at,
            ),
            self._session,
            self._client,
        )

    def _adopt_turn_from_created_event(self, event: TurnCreatedEvent) -> None:
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
        session: typing.Union["AsyncAgentSession", "AsyncAgentDraftSession"],
        client: AsyncTrueFoundryGateway,
    ) -> None:
        # Keep the raw value (which may be the OMIT sentinel) to forward to create_turn
        # unchanged; self._input is the list-or-None form used for local state/exposure.
        self._input_param = input
        self._input = list(input) if input is not None and input is not OMIT else None
        self._previous_turn_id = previous_turn_id
        self._session: typing.Union["AsyncAgentSession", "AsyncAgentDraftSession"] = session
        self._session_id: str = session.id
        self._client = client
        self._started: bool = False
        self._turn: typing.Optional[AsyncTurn] = None

    def __repr__(self) -> str:
        return f"AsyncPreparedTurn(session_id={self._session_id!r}, started={self._started!r})"

    # --- Properties that delegate to the inner AsyncTurn (None until execute is called) ---

    @property
    def session(self) -> typing.Union["AsyncAgentSession", "AsyncAgentDraftSession"]:
        """
        Returns
        -------
        typing.Union[AsyncAgentSession, AsyncAgentDraftSession]
            Parent session this prepared turn belongs to.
        """
        return self._session

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
    def id(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            None until ``execute()`` starts the turn.
        """
        return self._turn.id if self._turn is not None else None

    @property
    def previous_turn_id(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            None until ``execute()`` starts the turn.
        """
        return self._turn.previous_turn_id if self._turn is not None else None

    @property
    def state(self) -> typing.Optional[TurnState]:
        """
        Returns
        -------
        typing.Optional[TurnState]
            None until ``execute()`` starts the turn.
        """
        return self._turn.state if self._turn is not None else None

    @property
    def created_by_subject(self) -> typing.Optional[Subject]:
        """
        Returns
        -------
        typing.Optional[Subject]
            None until ``execute()`` starts the turn.
        """
        return self._turn.created_by_subject if self._turn is not None else None

    @property
    def created_at(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            None until ``execute()`` starts the turn.
        """
        return self._turn.created_at if self._turn is not None else None

    @property
    def input(self) -> typing.Optional[typing.List[TurnInputItem]]:
        """
        Returns
        -------
        typing.Optional[typing.List[TurnInputItem]]
            Staged input before ``execute()``; inner turn input after.
        """
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
        """
        Start the turn via ``create_turn_stream`` / ``create_turn``.

        Parameters
        ----------
        stream : bool
            Stream ``create_turn_stream`` SSE when true. Default true.
            When false, uses ``create_turn`` JSON then polls to terminal.
        poll_interval_ms : int
            Poll interval ms when ``stream=False``. Minimum 3000.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        TurnState
            Terminal turn state.

        Yields
        ------
        TurnStreamData
            SSE stream from create_turn_stream.
        """
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
        after_sequence_number: typing.Optional[int] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.AsyncIterator[TurnStreamData]:
        """
        Resubscribe via ``subscribe_to_turn`` after ``execute()``.

        Parameters
        ----------
        after_sequence_number : typing.Optional[int]
            Sequence number to resume SSE subscription after. Omit to resume via the
            Last-Event-Id header instead.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Yields
        ------
        TurnStreamData
            SSE stream items.
        """
        async for item in self._must_get_turn().stream(
            after_sequence_number=after_sequence_number, request_options=request_options
        ):
            yield item

    async def refresh(self, *, request_options: typing.Optional[RequestOptions] = None) -> "AsyncPreparedTurn":
        """
        Refetch from the server, update state in-place and return self.

        Parameters
        ----------
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AsyncPreparedTurn
            This prepared turn with updated state.
        """
        await self._must_get_turn().refresh(request_options=request_options)
        return self

    async def wait_for_completion(
        self,
        *,
        poll_interval_ms: int = 3000,
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
        return await self._must_get_turn().wait_for_completion(
            poll_interval_ms=poll_interval_ms, request_options=request_options
        )

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
        return await self._must_get_turn().cancel(request_options=request_options)

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
        """execute(stream=False) path: create_turn JSON returns the running turn; then poll."""
        response = await self._client.agents.sessions.create_turn(
            self._session_id,
            input=self._input_param,
            previous_turn_id=self._previous_turn_id,
            request_options=request_options,
        )
        self._adopt_turn_from_api(response.data)
        return await self._must_get_turn().wait_for_completion(
            poll_interval_ms=poll_interval_ms, request_options=request_options
        )

    async def _consume_stream(
        self, request_options: typing.Optional[RequestOptions]
    ) -> typing.AsyncIterator[TurnStreamData]:
        """Consume create_turn_stream SSE, adopting the inner Turn from the first turn.created."""
        async with self._client.agents.sessions.create_turn_stream(
            self._session_id,
            input=self._input_param,
            previous_turn_id=self._previous_turn_id,
            request_options=request_options,
        ) as sse:
            async for event in sse.with_metadata():
                sequence_number = parse_sequence_number(event.id)
                if isinstance(event.data, TurnCreatedEvent) and self._turn is None:
                    self._adopt_turn_from_created_event(event.data)
                elif self._turn is not None and isinstance(event.data, TurnDoneEvent):
                    self._replace_turn_state(event.data.state)
                yield TurnStreamData(sequence_number=sequence_number, event=event.data)

    def _must_get_turn(self) -> AsyncTurn:
        if self._turn is None:
            raise RuntimeError("Turn not started yet; call execute() first.")
        return self._turn

    def _adopt_turn_from_api(self, turn: RawTurn) -> None:
        self._turn = AsyncTurn(
            RawTurn(
                id=turn.id,
                session_id=turn.session_id,
                previous_turn_id=turn.previous_turn_id,
                input=turn.input if turn.input is not None else self._input,  # type: ignore[arg-type]
                state=turn.state,
                created_by_subject=turn.created_by_subject,
                created_at=turn.created_at,
            ),
            self._session,
            self._client,
        )

    def _adopt_turn_from_created_event(self, event: TurnCreatedEvent) -> None:
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
