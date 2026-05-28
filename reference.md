# Reference
## Agent Responses
<details><summary><code>client.agent.responses.<a href="src/truefoundry_gateway_sdk/agent/responses/client.py">create</a>(...) -> typing.Iterator[bytes]</code></summary>
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
from truefoundry_gateway_sdk import TruefoundryGateway, NamedAgentRunInput
from truefoundry_gateway_sdk.environment import TruefoundryGatewayEnvironment

client = TruefoundryGateway(
    token="<token>",
    environment=TruefoundryGatewayEnvironment.DEFAULT,
)

client.agent.responses.create(
    request=NamedAgentRunInput(
        agent_name="agent_name",
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

**request:** `AgentRunInput` 
    
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

<details><summary><code>client.agent.responses.<a href="src/truefoundry_gateway_sdk/agent/responses/client.py">cancel</a>(...) -> ResponsesCancelResponse</code></summary>
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

client.agent.responses.cancel(
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

<details><summary><code>client.agent.responses.<a href="src/truefoundry_gateway_sdk/agent/responses/client.py">get</a>(...) -> ResponsesGetResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the current state of an agent response.
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

client.agent.responses.get(
    response_id="responseId",
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

<details><summary><code>client.agent.responses.<a href="src/truefoundry_gateway_sdk/agent/responses/client.py">send_message</a>(...) -> ResponsesSendMessageResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Send approval decisions (allow/deny) to a running agent response awaiting user input.
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
from truefoundry_gateway_sdk import TruefoundryGateway, AgentApprovalDecisionMessage, AgentApprovalDecisionZero
from truefoundry_gateway_sdk.environment import TruefoundryGatewayEnvironment

client = TruefoundryGateway(
    token="<token>",
    environment=TruefoundryGatewayEnvironment.DEFAULT,
)

client.agent.responses.send_message(
    response_id="response_id",
    input=[
        AgentApprovalDecisionMessage(
            type="tool.approval",
            execution_id="execution_id",
            tool_call_id="tool_call_id",
            approval=AgentApprovalDecisionZero(
                status="allow",
            ),
        )
    ],
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

**input:** `typing.List[AgentApprovalDecisionMessage]` 
    
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

<details><summary><code>client.agent.responses.<a href="src/truefoundry_gateway_sdk/agent/responses/client.py">subscribe</a>(...) -> typing.Iterator[bytes]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Subscribe to a running agent response.
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

client.agent.responses.subscribe(
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

**sequence_id:** `typing.Optional[float]` 
    
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

