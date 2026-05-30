# Truefoundry Python Library

[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-Built%20with%20Fern-brightgreen)](https://buildwithfern.com?utm_source=github&utm_medium=github&utm_campaign=readme&utm_source=https%3A%2F%2Fgithub.com%2Ftruefoundry%2Ftruefoundry-gateway-python-sdk)
[![pypi](https://img.shields.io/pypi/v/truefoundry-gateway-sdk)](https://pypi.python.org/pypi/truefoundry-gateway-sdk)

This library provides convenient access to the TrueFoundry Gateway agent API. The gateway is a stateful, multi-tenant runtime that streams agent responses over Server-Sent Events.

Call the gateway directly — not via the control-plane `/api/llm` proxy. The tenant name is part of the base URL (e.g. `https://gateway.truefoundry.ai/<tenant>`) and is applied to every request.

> [!tip]
> You can ask questions about this SDK using DeepWiki
> - Python: [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/truefoundry/truefoundry-gateway-python-sdk)
> - TypeScript: [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/truefoundry/truefoundry-gateway-typescript-sdk)


## Table of Contents

- [Install](#install)
- [Quickstart](#quickstart)
- [Releasing](#releasing)
- [Installation](#installation)
- [Reference](#reference)
- [Usage](#usage)
- [Environments](#environments)
- [Async Client](#async-client)
- [Exception Handling](#exception-handling)
- [Streaming](#streaming)
- [Advanced](#advanced)
  - [Access Raw Response Data](#access-raw-response-data)
  - [Retries](#retries)
  - [Timeouts](#timeouts)
  - [Custom Client](#custom-client)
- [Contributing](#contributing)

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

## Installation

```sh
pip install truefoundry-gateway-sdk
```

## Reference

A full reference for this library is available [here](https://github.com/truefoundry/truefoundry-gateway-python-sdk/blob/HEAD/./reference.md).

## Usage

Instantiate and use the client with the following:

```python
from truefoundry_gateway_sdk import TruefoundryGateway, AgentResponsesInlineAgent

client = TruefoundryGateway(
    api_key="<token>",
)

client.agents.responses.create(
    request=AgentResponsesInlineAgent(
        model="model",
    ),
)
```

## Environments

This SDK allows you to configure different environments for API requests.

```python
from truefoundry_gateway_sdk import TruefoundryGateway
from truefoundry_gateway_sdk.environment import TruefoundryGatewayEnvironment

client = TruefoundryGateway(
    environment=TruefoundryGatewayEnvironment.DEFAULT,
)
```

## Async Client

The SDK also exports an `async` client so that you can make non-blocking calls to our API. Note that if you are constructing an Async httpx client class to pass into this client, use `httpx.AsyncClient()` instead of `httpx.Client()` (e.g. for the `httpx_client` parameter of this client).

```python
import asyncio

from truefoundry_gateway_sdk import AsyncTruefoundryGateway

client = AsyncTruefoundryGateway(
    api_key="<token>",
)


async def main() -> None:
    await client.agents.responses.create(
        request=AgentResponsesInlineAgent(
            model="model",
        ),
    )


asyncio.run(main())
```

## Exception Handling

When the API returns a non-success status code (4xx or 5xx response), a subclass of the following error
will be thrown.

```python
from truefoundry_gateway_sdk.core.api_error import ApiError

try:
    client.agents.responses.create(...)
except ApiError as e:
    print(e.status_code)
    print(e.body)
```

## Streaming

The SDK supports streaming responses, as well, the response will be a generator that you can loop over.

```python
from truefoundry_gateway_sdk import TruefoundryGateway, AgentResponsesInlineAgent

client = TruefoundryGateway(
    api_key="<token>",
)

client.agents.responses.create(
    request=AgentResponsesInlineAgent(
        model="model",
    ),
)
```

## Advanced

### Access Raw Response Data

The SDK provides access to raw response data, including headers, through the `.with_raw_response` property.
The `.with_raw_response` property returns a "raw" client that can be used to access the `.headers` and `.data` attributes.

```python
from truefoundry_gateway_sdk import TruefoundryGateway

client = TruefoundryGateway(...)
response = client.agents.responses.with_raw_response.create(...)
print(response.headers)  # access the response headers
print(response.status_code)  # access the response status code
print(response.data)  # access the underlying object
```

### Retries

The SDK is instrumented with automatic retries with exponential backoff. A request will be retried as long
as the request is deemed retryable and the number of retry attempts has not grown larger than the configured
retry limit (default: 2).

Which status codes are retried depends on the `retryStatusCodes` generator configuration:

**`legacy`** (current default): retries on
- [408](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408) (Timeout)
- [409](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/409) (Conflict)
- [429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429) (Too Many Requests)
- [5XX](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#server_error_responses) (All server errors, including 500)

**`recommended`**: retries on
- [408](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408) (Timeout)
- [409](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/409) (Conflict)
- [429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429) (Too Many Requests)
- [502](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502) (Bad Gateway)
- [503](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/503) (Service Unavailable)
- [504](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504) (Gateway Timeout)

Use the `max_retries` request option to configure this behavior.

```python
client.agents.responses.create(..., request_options={
    "max_retries": 1
})
```

### Timeouts

The SDK defaults to a 60 second timeout. You can configure this with a timeout option at the client or request level.

```python
from truefoundry_gateway_sdk import TruefoundryGateway

client = TruefoundryGateway(..., timeout=20.0)

# Override timeout for a specific method
client.agents.responses.create(..., request_options={
    "timeout_in_seconds": 1
})
```

### Custom Client

You can override the `httpx` client to customize it for your use-case. Some common use-cases include support for proxies
and transports.

```python
import httpx
from truefoundry_gateway_sdk import TruefoundryGateway

client = TruefoundryGateway(
    ...,
    httpx_client=httpx.Client(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically.
Additions made directly to this library would have to be moved over to our generation code,
otherwise they would be overwritten upon the next generated release. Feel free to open a PR as
a proof of concept, but know that we will not be able to merge it as-is. We suggest opening
an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
