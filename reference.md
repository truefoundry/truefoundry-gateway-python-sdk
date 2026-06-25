# Reference
## Agents Sessions
<details><summary><code>client.agents.sessions.<a href="src/truefoundry_gateway_sdk/agents/sessions/client.py">list</a>(...) -> SessionsListResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List sessions for an agent (newest first by default), keyset-paginated. Pass `page_token` to fetch the next page, keeping the other query params constant.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway
from truefoundry_gateway_sdk.agents.sessions import SessionsListRequestOrder

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.agents.sessions.list(
    agent_name="agent_name",
    limit=1,
    order=SessionsListRequestOrder.ASC,
    page_token="page_token",
    start_timestamp="start_timestamp",
    end_timestamp="end_timestamp",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**agent_name:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**order:** `typing.Optional[SessionsListRequestOrder]` 
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**start_timestamp:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**end_timestamp:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.sessions.<a href="src/truefoundry_gateway_sdk/agents/sessions/client.py">create</a>(...) -> SessionsCreateResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a session for an existing named agent.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.agents.sessions.create(
    agent_name="agent_name",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**agent_name:** `str` — Name of an existing agent in the tenant.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.sessions.<a href="src/truefoundry_gateway_sdk/agents/sessions/client.py">get</a>(...) -> SessionsGetResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a session by id. Visible to the session owner or a manager of the session agent.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.agents.sessions.get(
    session_id="sessionId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**session_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.sessions.<a href="src/truefoundry_gateway_sdk/agents/sessions/client.py">cancel</a>(...) -> SessionsCancelResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Cancel the running last turn for a session.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.agents.sessions.cancel(
    session_id="01arz3ndektsv4rrffq69g5fav.g",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**session_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.sessions.<a href="src/truefoundry_gateway_sdk/agents/sessions/client.py">list_turns</a>(...) -> SessionsListTurnsResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List turns for a session (newest first). Pagination walks the ancestor chain from the session last turn, or from the turn in page_token when continuing.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.agents.sessions.list_turns(
    session_id="01arz3ndektsv4rrffq69g5fav.g",
    page_token="page_token",
    limit=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**session_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.sessions.<a href="src/truefoundry_gateway_sdk/agents/sessions/client.py">create_turn</a>(...) -> typing.Iterator[bytes]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Start or continue a turn within a session. Responds with a Server-Sent Events stream.
Use `previous_turn_id` to chain to the session's last turn (defaults to `auto`).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.agents.sessions.create_turn(
    session_id="01arz3ndektsv4rrffq69g5fav.g",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**session_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**input:** `typing.Optional[typing.List[CreateTurnRequestInputItem]]` 
    
</dd>
</dl>

<dl>
<dd>

**previous_turn_id:** `typing.Optional[CreateTurnRequestPreviousTurnId]` — Defaults to 'auto' (chain to session last turn). Use 'null' for the session's first turn.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.sessions.<a href="src/truefoundry_gateway_sdk/agents/sessions/client.py">get_turn</a>(...) -> SessionsGetTurnResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a single turn by ID from Redis.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.agents.sessions.get_turn(
    session_id="01arz3ndektsv4rrffq69g5fav.g",
    turn_id="01arz3ndektsv4rrffq69g5fav.g.ab12cd",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**session_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**turn_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.sessions.<a href="src/truefoundry_gateway_sdk/agents/sessions/client.py">subscribe_to_turn</a>(...) -> typing.Iterator[bytes]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Subscribe to the live SSE stream for a turn. Pass after_sequence_number to resume after disconnect or server timeout, or send Last-Event-Id when after_sequence_number is omitted.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.agents.sessions.subscribe_to_turn(
    session_id="01arz3ndektsv4rrffq69g5fav.g",
    turn_id="01arz3ndektsv4rrffq69g5fav.g.ab12cd",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**session_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**turn_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**after_sequence_number:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.sessions.<a href="src/truefoundry_gateway_sdk/agents/sessions/client.py">list_turn_events</a>(...) -> SessionsListTurnEventsResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Paginated list of turn events from the Redis events stream.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway
from truefoundry_gateway_sdk.agents.sessions import SessionsListTurnEventsRequestOrder

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.agents.sessions.list_turn_events(
    session_id="01arz3ndektsv4rrffq69g5fav.g",
    turn_id="01arz3ndektsv4rrffq69g5fav.g.ab12cd",
    page_token="page_token",
    limit=1,
    order=SessionsListTurnEventsRequestOrder.ASC,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**session_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**turn_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**order:** `typing.Optional[SessionsListTurnEventsRequestOrder]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Internal Agents DraftSessions
<details><summary><code>client.internal.agents.draft_sessions.<a href="src/truefoundry_gateway_sdk/internal/agents/draft_sessions/client.py">list</a>(...) -> DraftSessionsListResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List the caller-owned draft sessions (newest first by default), keyset-paginated. Optionally filter by `agent_name`. Pass `page_token` to fetch the next page, keeping the other query params constant.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway
from truefoundry_gateway_sdk.internal.agents.draft_sessions import DraftSessionsListRequestOrder

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.internal.agents.draft_sessions.list(
    agent_name="agent_name",
    limit=1,
    order=DraftSessionsListRequestOrder.ASC,
    page_token="page_token",
    start_timestamp="start_timestamp",
    end_timestamp="end_timestamp",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**agent_name:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**order:** `typing.Optional[DraftSessionsListRequestOrder]` 
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**start_timestamp:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**end_timestamp:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.internal.agents.draft_sessions.<a href="src/truefoundry_gateway_sdk/internal/agents/draft_sessions/client.py">create</a>(...) -> DraftSessionsCreateResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a draft session holding an inline agent spec, optionally linked to a saved agent. Owner is the token subject.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway, AgentModelSpec
from truefoundry_gateway_sdk.internal.agents.draft_sessions import CreateDraftSessionRequestAgentSpec

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.internal.agents.draft_sessions.create(
    agent_spec=CreateDraftSessionRequestAgentSpec(
        model=AgentModelSpec(
            name="name",
        ),
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**agent_spec:** `CreateDraftSessionRequestAgentSpec` — Inline agent definition.
    
</dd>
</dl>

<dl>
<dd>

**agent_name:** `typing.Optional[str]` — Optionally link the draft to an existing saved agent in the tenant. Omit for a standalone draft.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.internal.agents.draft_sessions.<a href="src/truefoundry_gateway_sdk/internal/agents/draft_sessions/client.py">get</a>(...) -> DraftSessionsGetResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a draft session by id. Owner-only.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.internal.agents.draft_sessions.get(
    draft_session_id="draftSessionId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**draft_session_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.internal.agents.draft_sessions.<a href="src/truefoundry_gateway_sdk/internal/agents/draft_sessions/client.py">update</a>(...) -> DraftSessionsUpdateResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a draft session's inline spec. Owner-only. An empty body is a valid no-op that refreshes `updated_at`.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from truefoundry_gateway_sdk import TrueFoundryGateway

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.internal.agents.draft_sessions.update(
    draft_session_id="draftSessionId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**draft_session_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**agent_spec:** `typing.Optional[UpdateDraftSessionRequestAgentSpec]` — Replacement inline spec; never cleared.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

