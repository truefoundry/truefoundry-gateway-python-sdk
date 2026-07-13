from __future__ import annotations

import os
import typing

from ..core.pagination import AsyncPager, SyncPager
from .agent_session import AgentSession, AsyncAgentSession

if typing.TYPE_CHECKING:
    import httpx

    from ..client import AsyncTrueFoundryGateway, TrueFoundryGateway
    from ..core.logging import LogConfig, Logger
    from ..core.request_options import RequestOptions
    from ..types.list_sessions_order import ListSessionsOrder
    from ..types.list_sessions_response import ListSessionsResponse
    from ..types.session import Session as RawSession


def _wrap_sessions_pager(
    raw_pager: SyncPager[RawSession, ListSessionsResponse],
    client: TrueFoundryGateway,
) -> SyncPager[AgentSession, ListSessionsResponse]:
    wrapped_items = [AgentSession(s, client) for s in (raw_pager.items or [])]

    def get_next() -> typing.Optional[SyncPager[AgentSession, ListSessionsResponse]]:
        if raw_pager.get_next is None:
            return None
        next_raw = raw_pager.get_next()
        if next_raw is None:
            return None
        return _wrap_sessions_pager(next_raw, client)

    return SyncPager(
        get_next=get_next if raw_pager.has_next else None,
        has_next=raw_pager.has_next,
        items=wrapped_items,
        response=raw_pager.response,
    )


async def _async_wrap_sessions_pager(
    raw_pager: AsyncPager[RawSession, ListSessionsResponse],
    client: AsyncTrueFoundryGateway,
) -> AsyncPager[AsyncAgentSession, ListSessionsResponse]:
    wrapped_items = [AsyncAgentSession(s, client) for s in (raw_pager.items or [])]

    async def get_next() -> typing.Optional[AsyncPager[AsyncAgentSession, ListSessionsResponse]]:
        if raw_pager.get_next is None:
            return None
        next_raw = await raw_pager.get_next()
        if next_raw is None:
            return None
        return await _async_wrap_sessions_pager(next_raw, client)

    return AsyncPager(
        get_next=get_next if raw_pager.has_next else None,
        has_next=raw_pager.has_next,
        items=wrapped_items,
        response=raw_pager.response,
    )


class AgentSessionClient:
    """
    Entry-point for the high-level agent API. Wraps TrueFoundryGateway and returns
    enriched AgentSession objects instead of raw response types.
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
        from ..client import TrueFoundryGateway

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

    def create_session(
        self,
        *,
        agent_name: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AgentSession:
        """
        Create a new session for a named agent.

        Parameters
        ----------
        agent_name : str
            Name of the agent to create a session for.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AgentSession
            Session created.
        """
        response = self._client.agents.sessions.create(agent_name=agent_name, request_options=request_options)
        return AgentSession(response.data, self._client)

    def list_sessions(
        self,
        *,
        agent_name: str,
        limit: typing.Optional[int] = 10,
        order: typing.Optional[ListSessionsOrder] = None,
        page_token: typing.Optional[str] = None,
        start_timestamp: typing.Optional[str] = None,
        end_timestamp: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SyncPager[AgentSession, ListSessionsResponse]:
        """
        List sessions for an agent.

        Parameters
        ----------
        agent_name : str
            Name of the agent whose sessions to list.
        limit : typing.Optional[int]
            Page size. Default 10.
        order : typing.Optional[ListSessionsOrder]
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
        SyncPager[AgentSession, ListSessionsResponse]
            Paginated sessions.
        """
        raw_pager = self._client.agents.sessions.list(
            agent_name=agent_name,
            limit=limit,
            order=order,
            page_token=page_token,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            request_options=request_options,
        )
        return _wrap_sessions_pager(raw_pager, self._client)

    def get_session(
        self,
        session_id: str,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AgentSession:
        """
        Fetch a session by ID.

        Parameters
        ----------
        session_id : str
            Unique identifier of the session to fetch.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AgentSession
            Session data.
        """
        response = self._client.agents.sessions.get(session_id, request_options=request_options)
        return AgentSession(response.data, self._client)


class AsyncAgentSessionClient:
    """
    Async entry-point for the high-level agent API. Wraps AsyncTrueFoundryGateway and
    returns enriched AsyncAgentSession objects instead of raw response types.
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
        from ..client import AsyncTrueFoundryGateway

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

    async def create_session(
        self,
        *,
        agent_name: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncAgentSession:
        """
        Create a new session for a named agent.

        Parameters
        ----------
        agent_name : str
            Name of the agent to create a session for.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AsyncAgentSession
            Session created.
        """
        response = await self._client.agents.sessions.create(agent_name=agent_name, request_options=request_options)
        return AsyncAgentSession(response.data, self._client)

    async def list_sessions(
        self,
        *,
        agent_name: str,
        limit: typing.Optional[int] = 10,
        order: typing.Optional[ListSessionsOrder] = None,
        page_token: typing.Optional[str] = None,
        start_timestamp: typing.Optional[str] = None,
        end_timestamp: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncPager[AsyncAgentSession, ListSessionsResponse]:
        """
        List sessions for an agent.

        Parameters
        ----------
        agent_name : str
            Name of the agent whose sessions to list.
        limit : typing.Optional[int]
            Page size. Default 10.
        order : typing.Optional[ListSessionsOrder]
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
        AsyncPager[AsyncAgentSession, ListSessionsResponse]
            Paginated sessions.
        """
        raw_pager = await self._client.agents.sessions.list(
            agent_name=agent_name,
            limit=limit,
            order=order,
            page_token=page_token,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            request_options=request_options,
        )
        return await _async_wrap_sessions_pager(raw_pager, self._client)

    async def get_session(
        self,
        session_id: str,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncAgentSession:
        """
        Fetch a session by ID.

        Parameters
        ----------
        session_id : str
            Unique identifier of the session to fetch.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        AsyncAgentSession
            Session data.
        """
        response = await self._client.agents.sessions.get(session_id, request_options=request_options)
        return AsyncAgentSession(response.data, self._client)
