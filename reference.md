# Reference
## Agents Responses
<details><summary><code>client.agents.responses.<a href="src/truefoundry_gateway_sdk/agents/responses/client.py">create</a>(...) -> typing.Iterator[bytes]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Execute an agent in stateful mode (responses are stored server-side by default). Use Named (`agent_name`) or Inline (`model`) input. Continue a conversation with `previous_response_id`. Responds with a Server-Sent Events stream of `AgentResponseStreamingOutputEvent` objects.
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
from truefoundry_gateway_sdk import TruefoundryGateway, AgentResponsesInlineAgent
from truefoundry_gateway_sdk.environment import TruefoundryGatewayEnvironment

client = TruefoundryGateway(
    token="<token>",
    environment=TruefoundryGatewayEnvironment.DEFAULT,
)

client.agents.responses.create(
    request=AgentResponsesInlineAgent(
        model="model",
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

**request:** `AgentResponsesBody` 
    
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

<details><summary><code>client.agents.responses.<a href="src/truefoundry_gateway_sdk/agents/responses/client.py">cancel</a>(...) -> ResponsesCancelResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Cancel a running agent response. Requires the `response_id` returned from a prior stateful `/responses` call.
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
from truefoundry_gateway_sdk import TruefoundryGateway
from truefoundry_gateway_sdk.environment import TruefoundryGatewayEnvironment

client = TruefoundryGateway(
    token="<token>",
    environment=TruefoundryGatewayEnvironment.DEFAULT,
)

client.agents.responses.cancel(
    response_id="response_id",
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

**response_id:** `str` 
    
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

