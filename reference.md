# Reference
## Private Agents
<details><summary><code>client.private.agents.<a href="src/truefoundry_gateway_sdk/private/agents/client.py">download_sandbox_file</a>(...) -> typing.Iterator[bytes]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Download a file produced by an agent inside a sandbox.
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

client.private.agents.download_sandbox_file(
    sandbox_id="sandboxId",
    path="x",
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

**sandbox_id:** `str` — The sandbox containing the file.
    
</dd>
</dl>

<dl>
<dd>

**path:** `str` — Absolute path of the file inside the sandbox.
    
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

## Private Agents DraftSessions
<details><summary><code>client.private.agents.draft_sessions.<a href="src/truefoundry_gateway_sdk/private/agents/draft_sessions/client.py">list</a>(...) -> ListDraftSessionsResponse</code></summary>
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
from truefoundry_gateway_sdk import TrueFoundryGateway, ListDraftSessionsOrder

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.private.agents.draft_sessions.list(
    agent_name="agent_name",
    limit=1,
    order=ListDraftSessionsOrder.ASC,
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

**agent_name:** `typing.Optional[str]` — Filter to drafts linked to this saved agent. Omit to list all of the caller-owned drafts.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Page size. Defaults to 10, max 100.
    
</dd>
</dl>

<dl>
<dd>

**order:** `typing.Optional[ListDraftSessionsOrder]` — Sort draft sessions by creation time. Defaults to "desc".
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` — Opaque token from a previous response `next_page_token`.
    
</dd>
</dl>

<dl>
<dd>

**start_timestamp:** `typing.Optional[str]` — Inclusive lower bound on `created_at`. Defaults upstream to 30 min before `end_timestamp`.
    
</dd>
</dl>

<dl>
<dd>

**end_timestamp:** `typing.Optional[str]` — Inclusive upper bound on `created_at`. Defaults upstream to now.
    
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

<details><summary><code>client.private.agents.draft_sessions.<a href="src/truefoundry_gateway_sdk/private/agents/draft_sessions/client.py">create</a>(...) -> GetDraftSessionResponse</code></summary>
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
from truefoundry_gateway_sdk import TrueFoundryGateway, AgentSpec, Model

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.private.agents.draft_sessions.create(
    agent_spec=AgentSpec(
        model=Model(
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

**agent_spec:** `AgentSpec` 
    
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

<details><summary><code>client.private.agents.draft_sessions.<a href="src/truefoundry_gateway_sdk/private/agents/draft_sessions/client.py">get</a>(...) -> GetDraftSessionResponse</code></summary>
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

client.private.agents.draft_sessions.get(
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

**draft_session_id:** `str` — Draft session identifier.
    
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

<details><summary><code>client.private.agents.draft_sessions.<a href="src/truefoundry_gateway_sdk/private/agents/draft_sessions/client.py">update</a>(...) -> GetDraftSessionResponse</code></summary>
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

client.private.agents.draft_sessions.update(
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

**draft_session_id:** `str` — Draft session identifier.
    
</dd>
</dl>

<dl>
<dd>

**agent_spec:** `typing.Optional[AgentSpec]` 
    
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

## Private Agents Sessions
<details><summary><code>client.private.agents.sessions.<a href="src/truefoundry_gateway_sdk/private/agents/sessions/client.py">list</a>(...) -> ListSessionsResponse</code></summary>
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
from truefoundry_gateway_sdk import TrueFoundryGateway, ListSessionsOrder

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.private.agents.sessions.list(
    agent_name="agent_name",
    limit=1,
    order=ListSessionsOrder.ASC,
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

**agent_name:** `str` — Agent whose sessions to list. Must exist in the tenant.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Page size. Defaults to 10, max 100.
    
</dd>
</dl>

<dl>
<dd>

**order:** `typing.Optional[ListSessionsOrder]` — Sort sessions by creation time. Defaults to "desc".
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` — Opaque token from a previous response `next_page_token`.
    
</dd>
</dl>

<dl>
<dd>

**start_timestamp:** `typing.Optional[str]` — Inclusive lower bound on `created_at` (ISO-8601). Defaults upstream to 30 min before `end_timestamp`.
    
</dd>
</dl>

<dl>
<dd>

**end_timestamp:** `typing.Optional[str]` — Inclusive upper bound on `created_at` (ISO-8601). Defaults upstream to now.
    
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

<details><summary><code>client.private.agents.sessions.<a href="src/truefoundry_gateway_sdk/private/agents/sessions/client.py">create</a>(...) -> GetSessionResponse</code></summary>
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

client.private.agents.sessions.create(
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

<details><summary><code>client.private.agents.sessions.<a href="src/truefoundry_gateway_sdk/private/agents/sessions/client.py">get</a>(...) -> GetSessionResponse</code></summary>
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

client.private.agents.sessions.get(
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

**session_id:** `str` — Session identifier.
    
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

<details><summary><code>client.private.agents.sessions.<a href="src/truefoundry_gateway_sdk/private/agents/sessions/client.py">cancel</a>(...) -> CancelSessionResponse</code></summary>
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

client.private.agents.sessions.cancel(
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

<details><summary><code>client.private.agents.sessions.<a href="src/truefoundry_gateway_sdk/private/agents/sessions/client.py">list_turns</a>(...) -> ListTurnsResponse</code></summary>
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

client.private.agents.sessions.list_turns(
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

**limit:** `typing.Optional[int]` — Page size. Defaults to 10, max 25.
    
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

<details><summary><code>client.private.agents.sessions.<a href="src/truefoundry_gateway_sdk/private/agents/sessions/client.py">create_turn</a>(...) -> typing.Iterator[bytes]</code></summary>
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

client.private.agents.sessions.create_turn(
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

**input:** `typing.Optional[typing.List[TurnInputItem]]` 
    
</dd>
</dl>

<dl>
<dd>

**previous_turn_id:** `typing.Optional[PreviousTurnIdInput]` 
    
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

<details><summary><code>client.private.agents.sessions.<a href="src/truefoundry_gateway_sdk/private/agents/sessions/client.py">get_turn</a>(...) -> GetTurnResponse</code></summary>
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

client.private.agents.sessions.get_turn(
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

<details><summary><code>client.private.agents.sessions.<a href="src/truefoundry_gateway_sdk/private/agents/sessions/client.py">subscribe_to_turn</a>(...) -> typing.Iterator[bytes]</code></summary>
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

client.private.agents.sessions.subscribe_to_turn(
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

<details><summary><code>client.private.agents.sessions.<a href="src/truefoundry_gateway_sdk/private/agents/sessions/client.py">list_turn_events</a>(...) -> ListEventsResponse</code></summary>
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
from truefoundry_gateway_sdk import TrueFoundryGateway, ListEventsOrder

client = TrueFoundryGateway(
    api_key="<token>",
    base_url="https://yourhost.com/path/to/api",
)

client.private.agents.sessions.list_turn_events(
    session_id="01arz3ndektsv4rrffq69g5fav.g",
    turn_id="01arz3ndektsv4rrffq69g5fav.g.ab12cd",
    page_token="page_token",
    limit=1,
    order=ListEventsOrder.ASC,
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

**limit:** `typing.Optional[int]` — Page size. Defaults to 25, max 25.
    
</dd>
</dl>

<dl>
<dd>

**order:** `typing.Optional[ListEventsOrder]` — Sort events by creation time. Defaults to "asc".
    
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

