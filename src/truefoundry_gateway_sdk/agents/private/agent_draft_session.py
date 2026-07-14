from __future__ import annotations

import typing

from ..agent_session import AsyncBaseAgentSession, BaseAgentSession

if typing.TYPE_CHECKING:
    from ...client import AsyncTrueFoundryGateway, TrueFoundryGateway
    from ...core.request_options import RequestOptions
    from ...types.agent_spec import AgentSpec
    from ...types.draft_session import DraftSession


class AgentDraftSession(BaseAgentSession):
    """
    A draft session enriched with convenience methods inherited from BaseAgentSession, plus
    an ``update()`` method to mutate the inline agent spec.
    """

    def __init__(self, session: DraftSession, client: TrueFoundryGateway) -> None:
        super().__init__(
            id=session.id,
            title=session.title,
            created_by_subject=session.created_by_subject,
            created_at=session.created_at,
            updated_at=session.updated_at,
            client=client,
        )
        self._agent_name: typing.Optional[str] = session.agent_name
        self._agent_spec: AgentSpec = session.agent_spec

    def __repr__(self) -> str:
        return f"AgentDraftSession(id={self._id!r}, agent_name={self._agent_name!r})"

    @property
    def agent_name(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            Name of the agent this draft session is linked to, if any.
        """
        return self._agent_name

    @property
    def agent_spec(self) -> AgentSpec:
        """
        Returns
        -------
        AgentSpec
            The inline agent specification for this draft session.
        """
        return self._agent_spec

    def update(
        self,
        agent_spec: AgentSpec,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> None:
        """
        Update the inline agent spec for this draft session.

        Calls ``PATCH v1/agents/draft-sessions/{id}`` and syncs ``agent_spec``
        and ``updated_at`` on this object in place.

        Parameters
        ----------
        agent_spec : AgentSpec
            The new agent specification to store.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        None
        """
        response = self._client.agents.private.draft_sessions.update(
            self._id,
            agent_spec=agent_spec,
            request_options=request_options,
        )
        self._agent_spec = response.data.agent_spec
        self._updated_at = response.data.updated_at


class AsyncAgentDraftSession(AsyncBaseAgentSession):
    """
    Async version of AgentDraftSession.
    """

    def __init__(self, session: DraftSession, client: AsyncTrueFoundryGateway) -> None:
        super().__init__(
            id=session.id,
            title=session.title,
            created_by_subject=session.created_by_subject,
            created_at=session.created_at,
            updated_at=session.updated_at,
            client=client,
        )
        self._agent_name: typing.Optional[str] = session.agent_name
        self._agent_spec: AgentSpec = session.agent_spec

    def __repr__(self) -> str:
        return f"AsyncAgentDraftSession(id={self._id!r}, agent_name={self._agent_name!r})"

    @property
    def agent_name(self) -> typing.Optional[str]:
        """
        Returns
        -------
        typing.Optional[str]
            Name of the agent this draft session is linked to, if any.
        """
        return self._agent_name

    @property
    def agent_spec(self) -> AgentSpec:
        """
        Returns
        -------
        AgentSpec
            The inline agent specification for this draft session.
        """
        return self._agent_spec

    async def update(
        self,
        agent_spec: AgentSpec,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> None:
        """
        Update the inline agent spec for this draft session.

        Calls ``PATCH v1/agents/draft-sessions/{id}`` and syncs ``agent_spec``
        and ``updated_at`` on this object in place.

        Parameters
        ----------
        agent_spec : AgentSpec
            The new agent specification to store.
        request_options : typing.Optional[RequestOptions]
            Overrides client timeout, retries, headers, and stream reconnect.

        Returns
        -------
        None
        """
        response = await self._client.agents.private.draft_sessions.update(
            self._id,
            agent_spec=agent_spec,
            request_options=request_options,
        )
        self._agent_spec = response.data.agent_spec
        self._updated_at = response.data.updated_at
