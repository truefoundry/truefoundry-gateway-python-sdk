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
    from ..types.session_event_item import SessionEventItem
    from ..types.turn import Turn as RawTurn
    from ..types.turn_input_item import TurnInputItem
    from .agent_session import AgentSession, AsyncAgentSession
    from .private.agent_draft_session import AgentDraftSession, AsyncAgentDraftSession

    SyncSessionOwner = typing.Union[AgentSession, AgentDraftSession]
    AsyncSessionOwner = typing.Union[AsyncAgentSession, AsyncAgentDraftSession]


def _wrap_turns_pager(
    raw_pager: SyncPager[RawTurn, ListTurnsResponse],
    owner: SyncSessionOwner,
    client: TrueFoundryGateway,
) -> SyncPager[Turn, ListTurnsResponse]:
    wrapped_items = [Turn(t, owner, client) for t in (raw_pager.items or [])]

    def get_next() -> typing.Optional[SyncPager[Turn, ListTurnsResponse]]:
        if raw_pager.get_next is None:
            return None
        next_raw = raw_pager.get_next()
        if next_raw is None:
            return None
        return _wrap_turns_pager(next_raw, owner, client)

    return SyncPager(
        get_next=get_next if raw_pager.has_next else None,
        has_next=raw_pager.has_next,
        items=wrapped_items,
        response=raw_pager.response,
    )


async def _async_wrap_turns_pager(
    raw_pager: AsyncPager[RawTurn, ListTurnsResponse],
    owner: AsyncSessionOwner,
    client: AsyncTrueFoundryGateway,
) -> AsyncPager[AsyncTurn, ListTurnsResponse]:
    wrapped_items = [AsyncTurn(t, owner, client) for t in (raw_pager.items or [])]

    async def get_next() -> typing.Optional[AsyncPager[AsyncTurn, ListTurnsResponse]]:
        if raw_pager.get_next is None:
            return None
        next_raw = await raw_pager.get_next()
        if next_raw is None:
            return None
        return await _async_wrap_turns_pager(next_raw, owner, client)

    return AsyncPager(
        get_next=get_next if raw_pager.has_next else None,
        has_next=raw_pager.has_next,
        items=wrapped_items,
        response=raw_pager.response,
    )


class SessionMixin:
    """
    Shared turn behavior keyed by a session id. Both :class:`AgentSession` and
    :class:`AgentDraftSession` hold a SessionMixin and delegate prepare_turn / list_turns /
    get_turn / cancel / list_events to it, so the two session wrappers expose identical turn
    operations without duplicating logic.

    The owning wrapper is NOT stored on the mixin (that back-reference would form an
    ``AgentSession`` <-> ``SessionMixin`` cycle that outlives both). Instead the wrapper passes
    itself as the first argument to each turn-producing method, so turns still expose the
    enriched wrapper (with ``agent_name``, ``title``, etc.) as ``turn.session``.
    """

    def __init__(self, id: str, client: TrueFoundryGateway) -> None:
        self._id = id
        self._client = client

    def prepare_turn(
        self,
        owner: SyncSessionOwner,
        *,
        input: typing.Optional[typing.Sequence[TurnInputItem]] = None,
        previous_turn_id: typing.Optional[PreviousTurnIdInput] = None,
    ) -> PreparedTurn:
        """
        Stage a turn locally; call ``execute()`` to start ``create_turn``.

        Parameters
        ----------
        owner : SyncSessionOwner
            Enriched wrapper surfaced as ``turn.session`` on the resulting turn.
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
            session=owner,
            client=self._client,
        )

    def list_turns(
        self,
        owner: SyncSessionOwner,
        *,
        page_token: typing.Optional[str] = None,
        limit: typing.Optional[int] = 10,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SyncPager[Turn, ListTurnsResponse]:
        """
        List turns in this session.

        Parameters
        ----------
        owner : SyncSessionOwner
            Enriched wrapper surfaced as ``turn.session`` on each listed turn.
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
        return _wrap_turns_pager(raw_pager, owner, self._client)

    def get_turn(
        self,
        owner: SyncSessionOwner,
        turn_id: str,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> Turn:
        """
        Fetch a turn by ID.

        Parameters
        ----------
        owner : SyncSessionOwner
            Enriched wrapper surfaced as ``turn.session`` on the resulting turn.
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
        return Turn(response.data, owner, self._client)

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


class AsyncSessionMixin:
    """
    Async version of :class:`SessionMixin`. Same delegation contract; the owning wrapper passes
    itself as the first argument to each turn-producing method so turns expose the enriched
    wrapper as ``turn.session``.
    """

    def __init__(self, id: str, client: AsyncTrueFoundryGateway) -> None:
        self._id = id
        self._client = client

    def prepare_turn(
        self,
        owner: AsyncSessionOwner,
        *,
        input: typing.Optional[typing.Sequence[TurnInputItem]] = None,
        previous_turn_id: typing.Optional[PreviousTurnIdInput] = None,
    ) -> AsyncPreparedTurn:
        """
        Stage a turn locally; call ``execute()`` to start ``create_turn``.

        Parameters
        ----------
        owner : AsyncSessionOwner
            Enriched wrapper surfaced as ``turn.session`` on the resulting turn.
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
            session=owner,
            client=self._client,
        )

    async def list_turns(
        self,
        owner: AsyncSessionOwner,
        *,
        page_token: typing.Optional[str] = None,
        limit: typing.Optional[int] = 10,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncPager[AsyncTurn, ListTurnsResponse]:
        """
        List turns in this session.

        Parameters
        ----------
        owner : AsyncSessionOwner
            Enriched wrapper surfaced as ``turn.session`` on each listed turn.
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
        return await _async_wrap_turns_pager(raw_pager, owner, self._client)

    async def get_turn(
        self,
        owner: AsyncSessionOwner,
        turn_id: str,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncTurn:
        """
        Fetch a turn by ID.

        Parameters
        ----------
        owner : AsyncSessionOwner
            Enriched wrapper surfaced as ``turn.session`` on the resulting turn.
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
        return AsyncTurn(response.data, owner, self._client)

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
