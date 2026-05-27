# truefoundry-gateway-sdk (Python)

> ⚠️ This repository is **auto-generated** by [Fern](https://buildwithfern.com/)
> from [`truefoundry/truefoundry-gateway-fern-config`](https://github.com/truefoundry/truefoundry-gateway-fern-config).
>
> All hand edits will be overwritten on the next SDK release except for the
> paths listed in [`.fernignore`](./.fernignore). To change generated code,
> edit the OpenAPI spec / overrides / generator config in the fern-config
> repo and cut a new release.

`truefoundry-gateway-sdk` is the Python client for the TrueFoundry Gateway
agent API — a stateful, streaming runtime exposed at
`https://gateway.truefoundry.ai/<tenant>/agent/*`.

## Install

```sh
pip install truefoundry-gateway-sdk
```

## Quickstart

```python
from truefoundry_gateway_sdk import (
    AgentInputUserMessage,
    NamedAgentRunInput,
    TruefoundryGateway,
)

client = TruefoundryGateway(
    base_url="https://gateway.truefoundry.ai/<tenant>",
    token="<TFY_API_KEY>",
)

for event in client.agent.responses.create(
    request=NamedAgentRunInput(
        agent_name="my-agent",
        input=[AgentInputUserMessage(role="user", content="hi")],
    ),
):
    print(event)
```

`AsyncTruefoundryGateway` provides the same surface with `async`/`await`.

## Releasing

Releases are cut from
[`truefoundry/truefoundry-gateway-fern-config`](https://github.com/truefoundry/truefoundry-gateway-fern-config)
by pushing a `v*` tag there. The Fern workflow regenerates this repo onto a
`release-v<version>` branch and publishes the wheel to PyPI in the same job.
