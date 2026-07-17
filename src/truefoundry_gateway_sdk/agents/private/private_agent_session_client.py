from __future__ import annotations

import os
import typing

from ...core.pagination import AsyncPager, SyncPager
from ..agent_session import AgentSession, AsyncAgentSession
from .agent_draft_session import AgentDraftSession, AsyncAgentDraftSession

if typing.TYPE_CHECKING:
    import httpx
    from ...client import AsyncTrueFoundryGateway, TrueFoundryGateway
    from ...core.logging import LogConfig, Logger
    from ...core.request_options import RequestOptions
    from ...types.agent_spec import AgentSpec
    from ...types.draft_session import DraftSession as RawDraftSession
    from ...types.list_draft_sessions_order import ListDraftSessionsOrder
    from ...types.list_draft_sessions_response import ListDraftSessionsResponse
    from ...types.list_owned_sessions_order import ListOwnedSessionsOrder
    from ...types.list_owned_sessions_response import ListOwnedSessionsResponse
    from ...types.list_owned_sessions_response_data_item import ListOwnedSessionsResponseDataItem


def _wrap_draft_sessions_pager(
    raw_pager: SyncPager[RawDraftSession, ListDraftSessionsResponse],
    client: TrueFoundryGateway,
) -> SyncPager[AgentDraftSession, ListDraftSessionsResponse]:
    wrapped_items = [AgentDraftSession(d, client) for d in (raw_pager.items or [])]

    def get_next() -> typing.Optional[SyncPager[AgentDraftSession, ListDraftSessionsResponse]]:
        if raw_pager.get_next is None:
            return None
        next_raw = raw_pager.get_next()
        if next_raw is None:
            return None
        return _wrap_draft_sessions_pager(next_raw, client)

    return SyncPager(
        get_next=get_next if raw_pager.has_next else None,
        has_next=raw_pager.has_next,
        items=wrapped_items,
        response=raw_pager.response,
    )


def _wrap_owned_session(
    raw: ListOwnedSessionsResponseDataItem,
    client: TrueFoundryGateway,
) -> typing.Union[AgentSession, AgentDraftSession]:
    # Dispatch a raw owned-session union member into its enriched wrapper, keyed off the `type` discriminant.
    if raw.type == "session/draft":
        return AgentDraftSession(raw, client)
    if raw.type == "session":
        return AgentSession(raw, client)
    raise ValueError(f"Unknown owned session type: {raw.type!r}")


def _wrap_owned_sessions_pager(
    raw_pager: SyncPager[ListOwnedSessionsResponseDataItem, ListOwnedSessionsResponse],
    client: TrueFoundryGateway,
) -> SyncPager[typing.Union[AgentSession, AgentDraftSession], ListOwnedSessionsResponse]:
    wrapped_items = [_wrap_owned_session(s, client) for s in (raw_pager.items or [])]

    def get_next() -> typing.Optional[
        SyncPager[typing.Union[AgentSession, AgentDraftSession], ListOwnedSessionsResponse]
    ]:
        if raw_pager.get_next is None:
            return None
        next_raw = raw_pager.get_next()
        if next_raw is None:
            return None
        return _wrap_owned_sessions_pager(next_raw, client)

    return SyncPager(
        get_next=get_next if raw_pager.has_next else None,
        has_next=raw_pager.has_next,
        items=wrapped_items,
        response=raw_pager.response,
    )


async def _async_wrap_draft_sessions_pager(
    raw_pager: AsyncPager[RawDraftSession, ListDraftSessionsResponse],
    client: AsyncTrueFoundryGateway,
) -> AsyncPager[AsyncAgentDraftSession, ListDraftSessionsResponse]:
    wrapped_items = [AsyncAgentDraftSession(d, client) for d in (raw_pager.items or [])]

    async def get_next() -> typing.Optional[AsyncPager[AsyncAgentDraftSession, ListDraftSessionsResponse]]:
        if raw_pager.get_next is None:
            return None
        next_raw = await raw_pager.get_next()
        if next_raw is None:
            return None
        return await _async_wrap_draft_sessions_pager(next_raw, client)

    return AsyncPager(
        get_next=get_next if raw_pager.has_next else None,
        has_next=raw_pager.has_next,
        items=wrapped_items,
        response=raw_pager.response,
    )


def _async_wrap_owned_session(
    raw: ListOwnedSessionsResponseDataItem,
    client: AsyncTrueFoundryGateway,
) -> typing.Union[AsyncAgentSession, AsyncAgentDraftSession]:
    # Dispatch a raw owned-session union member into its enriched wrapper, keyed off the `type` discriminant.
    if raw.type == "session/draft":
        return AsyncAgentDraftSession(raw, client)
    if raw.type == "session":
        return AsyncAgentSession(raw, client)
    raise ValueError(f"Unknown owned session type: {raw.type!r}")


async def _async_wrap_owned_sessions_pager(
    raw_pager: AsyncPager[ListOwnedSessionsResponseDataItem, ListOwnedSessionsResponse],
    client: AsyncTrueFoundryGateway,
) -> AsyncPager[typing.Union[AsyncAgentSession, AsyncAgentDraftSession], ListOwnedSessionsResponse]:
    wrapped_items = [_async_wrap_owned_session(s, client) for s in (raw_pager.items or [])]

    async def get_next() -> typing.Optional[
        AsyncPager[typing.Union[AsyncAgentSession, AsyncAgentDraftSession], ListOwnedSessionsResponse]
    ]:
        if raw_pager.get_next is None:
            return None
        next_raw = await raw_pager.get_next()
        if next_raw is None:
            return None
        return await _async_wrap_owned_sessions_pager(next_raw, client)

    return AsyncPager(
        get_next=get_next if raw_pager.has_next else None,
        has_next=raw_pager.has_next,
        items=wrapped_items,
        response=raw_pager.response,
    )


class PrivateAgentSessionClient:
    """
    High-level client for caller-scoped agent session internals: draft session create/get and
    listings that span a subject's saved sessions and drafts, returning enriched
    :class:`AgentSession` / :class:`AgentDraftSession` objects instead of raw response types.
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: typing.Optional[typing.Union[str, typing.Callable[[], str]]] = os.getenv("TFY_API_KEY"),
        headers: typing.Optional[typing.Dict[str, str]] = None,
        timeout: typing.Optional[float] = None,
        max_retries: typing.Optional[int] = None,
        follow_redirects: typing.Optional[bool] = True,
        httpx_client: typing.Optional[httpx.Client] = None,
        logging: typing.Optional[typing.Union[LogConfig, Logger]] = None,
    ) -> None:
        from ...client import TrueFoundryGateway

        self._client = TrueFoundryGateway(
            base_url=base_url,
            api_key=api_key,
            headers=headers,
            timeout=timeout,
            max_retries=max_retries,
            follow_redirects=follow_redirects,
            httpx_client=httpx_client,
            logging=logging,
        )

    def create_draft_session(
        self,
        *,
        agent_spec: AgentSpec,
        agent_name: typing.Optional[str] = None,
        tfy_metadata: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AgentDraftSession:
        """
        Create a draft session holding an inline agent spec, optionally linked to a saved agent.

        Parameters
        ----------
        agent_spec : AgentSpec
            Inline agent spec held by the draft.
        agent_name : typing.Optional[str]
            Optionally link the draft to an existing saved agent. Omit for a standalone draft.
        tfy_metadata : typing.Optional[str]
            Optional request metadata (x-tfy-metadata) persisted at creation.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AgentDraftSession
            The created draft session.
        """
        response = self._client.agents.private.draft_sessions.create(
            agent_spec=agent_spec,
            agent_name=agent_name,
            tfy_metadata=tfy_metadata,
            request_options=request_options,
        )
        return AgentDraftSession(response.data, self._client)

    def get_draft_session(
        self,
        draft_session_id: str,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AgentDraftSession:
        """
        Fetch a draft session by ID (owner-only).

        Parameters
        ----------
        draft_session_id : str
            Unique identifier of the draft session to fetch.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AgentDraftSession
            Draft session data.
        """
        response = self._client.agents.private.draft_sessions.get(draft_session_id, request_options=request_options)
        return AgentDraftSession(response.data, self._client)

    def list_draft_sessions(
        self,
        *,
        agent_name: typing.Optional[str] = None,
        limit: typing.Optional[int] = 10,
        order: typing.Optional[ListDraftSessionsOrder] = None,
        page_token: typing.Optional[str] = None,
        start_timestamp: typing.Optional[str] = None,
        end_timestamp: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SyncPager[AgentDraftSession, ListDraftSessionsResponse]:
        """
        List the caller-owned draft sessions (newest first by default).

        Parameters
        ----------
        agent_name : typing.Optional[str]
            Filter to drafts linked to this saved agent. Omit for all owned drafts.
        limit : typing.Optional[int]
            Page size. Default 10.
        order : typing.Optional[ListDraftSessionsOrder]
            Sort by creation time. Default ``desc``.
        page_token : typing.Optional[str]
            Token from the previous response ``next_page_token``.
        start_timestamp : typing.Optional[str]
            Inclusive lower bound on ``created_at`` (ISO-8601).
        end_timestamp : typing.Optional[str]
            Inclusive upper bound on ``created_at`` (ISO-8601).
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        SyncPager[AgentDraftSession, ListDraftSessionsResponse]
            Paginated draft sessions.
        """
        raw_pager = self._client.agents.private.draft_sessions.list(
            agent_name=agent_name,
            limit=limit,
            order=order,
            page_token=page_token,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            request_options=request_options,
        )
        return _wrap_draft_sessions_pager(raw_pager, self._client)

    def list_owned_sessions(
        self,
        *,
        agent_name: typing.Optional[str] = None,
        limit: typing.Optional[int] = 10,
        order: typing.Optional[ListOwnedSessionsOrder] = None,
        page_token: typing.Optional[str] = None,
        start_timestamp: typing.Optional[str] = None,
        end_timestamp: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SyncPager[typing.Union[AgentSession, AgentDraftSession], ListOwnedSessionsResponse]:
        """
        List all sessions owned by the caller, spanning both saved sessions and drafts (newest first by default).

        Parameters
        ----------
        agent_name : typing.Optional[str]
            Filter to sessions linked to this saved agent. Omit for all owned sessions.
        limit : typing.Optional[int]
            Page size. Default 10.
        order : typing.Optional[ListOwnedSessionsOrder]
            Sort by creation time. Default ``desc``.
        page_token : typing.Optional[str]
            Token from the previous response ``next_page_token``.
        start_timestamp : typing.Optional[str]
            Inclusive lower bound on ``created_at`` (ISO-8601).
        end_timestamp : typing.Optional[str]
            Inclusive upper bound on ``created_at`` (ISO-8601).
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        SyncPager[typing.Union[AgentSession, AgentDraftSession], ListOwnedSessionsResponse]
            Paginated owned sessions.
        """
        raw_pager = self._client.agents.private.sessions.list_owned_sessions(
            agent_name=agent_name,
            limit=limit,
            order=order,
            page_token=page_token,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            request_options=request_options,
        )
        return _wrap_owned_sessions_pager(raw_pager, self._client)


class AsyncPrivateAgentSessionClient:
    """
    Async version of PrivateAgentSessionClient.
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: typing.Optional[typing.Union[str, typing.Callable[[], str]]] = os.getenv("TFY_API_KEY"),
        headers: typing.Optional[typing.Dict[str, str]] = None,
        async_token: typing.Optional[typing.Callable[[], typing.Awaitable[str]]] = None,
        timeout: typing.Optional[float] = None,
        max_retries: typing.Optional[int] = None,
        follow_redirects: typing.Optional[bool] = True,
        httpx_client: typing.Optional[httpx.AsyncClient] = None,
        logging: typing.Optional[typing.Union[LogConfig, Logger]] = None,
    ) -> None:
        from ...client import AsyncTrueFoundryGateway

        self._client = AsyncTrueFoundryGateway(
            base_url=base_url,
            api_key=api_key,
            headers=headers,
            async_token=async_token,
            timeout=timeout,
            max_retries=max_retries,
            follow_redirects=follow_redirects,
            httpx_client=httpx_client,
            logging=logging,
        )

    async def create_draft_session(
        self,
        *,
        agent_spec: AgentSpec,
        agent_name: typing.Optional[str] = None,
        tfy_metadata: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncAgentDraftSession:
        """
        Create a draft session holding an inline agent spec, optionally linked to a saved agent.

        Parameters
        ----------
        agent_spec : AgentSpec
            Inline agent spec held by the draft.
        agent_name : typing.Optional[str]
            Optionally link the draft to an existing saved agent. Omit for a standalone draft.
        tfy_metadata : typing.Optional[str]
            Optional request metadata (x-tfy-metadata) persisted at creation.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AsyncAgentDraftSession
            The created draft session.
        """
        response = await self._client.agents.private.draft_sessions.create(
            agent_spec=agent_spec,
            agent_name=agent_name,
            tfy_metadata=tfy_metadata,
            request_options=request_options,
        )
        return AsyncAgentDraftSession(response.data, self._client)

    async def get_draft_session(
        self,
        draft_session_id: str,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncAgentDraftSession:
        """
        Fetch a draft session by ID (owner-only).

        Parameters
        ----------
        draft_session_id : str
            Unique identifier of the draft session to fetch.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AsyncAgentDraftSession
            Draft session data.
        """
        response = await self._client.agents.private.draft_sessions.get(
            draft_session_id, request_options=request_options
        )
        return AsyncAgentDraftSession(response.data, self._client)

    async def list_draft_sessions(
        self,
        *,
        agent_name: typing.Optional[str] = None,
        limit: typing.Optional[int] = 10,
        order: typing.Optional[ListDraftSessionsOrder] = None,
        page_token: typing.Optional[str] = None,
        start_timestamp: typing.Optional[str] = None,
        end_timestamp: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncPager[AsyncAgentDraftSession, ListDraftSessionsResponse]:
        """
        List the caller-owned draft sessions (newest first by default).

        Parameters
        ----------
        agent_name : typing.Optional[str]
            Filter to drafts linked to this saved agent. Omit for all owned drafts.
        limit : typing.Optional[int]
            Page size. Default 10.
        order : typing.Optional[ListDraftSessionsOrder]
            Sort by creation time. Default ``desc``.
        page_token : typing.Optional[str]
            Token from the previous response ``next_page_token``.
        start_timestamp : typing.Optional[str]
            Inclusive lower bound on ``created_at`` (ISO-8601).
        end_timestamp : typing.Optional[str]
            Inclusive upper bound on ``created_at`` (ISO-8601).
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AsyncPager[AsyncAgentDraftSession, ListDraftSessionsResponse]
            Paginated draft sessions.
        """
        raw_pager = await self._client.agents.private.draft_sessions.list(
            agent_name=agent_name,
            limit=limit,
            order=order,
            page_token=page_token,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            request_options=request_options,
        )
        return await _async_wrap_draft_sessions_pager(raw_pager, self._client)

    async def list_owned_sessions(
        self,
        *,
        agent_name: typing.Optional[str] = None,
        limit: typing.Optional[int] = 10,
        order: typing.Optional[ListOwnedSessionsOrder] = None,
        page_token: typing.Optional[str] = None,
        start_timestamp: typing.Optional[str] = None,
        end_timestamp: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncPager[typing.Union[AsyncAgentSession, AsyncAgentDraftSession], ListOwnedSessionsResponse]:
        """
        List all sessions owned by the caller, spanning both saved sessions and drafts (newest first by default).

        Parameters
        ----------
        agent_name : typing.Optional[str]
            Filter to sessions linked to this saved agent. Omit for all owned sessions.
        limit : typing.Optional[int]
            Page size. Default 10.
        order : typing.Optional[ListOwnedSessionsOrder]
            Sort by creation time. Default ``desc``.
        page_token : typing.Optional[str]
            Token from the previous response ``next_page_token``.
        start_timestamp : typing.Optional[str]
            Inclusive lower bound on ``created_at`` (ISO-8601).
        end_timestamp : typing.Optional[str]
            Inclusive upper bound on ``created_at`` (ISO-8601).
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AsyncPager[typing.Union[AsyncAgentSession, AsyncAgentDraftSession], ListOwnedSessionsResponse]
            Paginated owned sessions.
        """
        raw_pager = await self._client.agents.private.sessions.list_owned_sessions(
            agent_name=agent_name,
            limit=limit,
            order=order,
            page_token=page_token,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            request_options=request_options,
        )
        return await _async_wrap_owned_sessions_pager(raw_pager, self._client)
