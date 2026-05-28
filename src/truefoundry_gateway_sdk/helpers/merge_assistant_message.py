"""
Fold ``agent.message`` assistant-role chunks (``AgentLlmMessageDelta``) emitted
by ``client.agents.responses.create`` into a single rolling
``EnrichedAssistantMessage``.

Pure reducer — pass the previous result back in for each chunk. Caller
responsibilities (not handled here):

- Filter with :func:`is_assistant_delta` (skip tool-role messages and lifecycle events).
- Reset ``current`` to ``None`` after each chunk with ``finish_reason`` (multiple turns per stream).
- Key merge state by ``execution_id`` when parent/sub-agent streams interleave.

Type names mirror the gateway's ``src/agent/LLMTypes.ts``:
``EnrichedAssistantMessage`` (tool_calls carry ``tool_info``),
``EnrichedToolCall``, ``ThinkingBlockUnion``. Behavior mirrors the gateway's
``accumulateTokensFromChunk`` reducer plus SDK-only fields (``refusal``,
``tool_info``). ``reasoning_content`` is dropped (SSE-only; use
``thinking_blocks`` instead).

Discrimination of thinking blocks and tool-call deltas is done via the ``type``
and ``index`` fields on the incoming objects, so this helper does not depend on
Fern-generated discriminator class names that may shift across spec revisions.
"""

from __future__ import annotations

import typing

import pydantic

from ..types import (
    AgentExtendedDeltaToolCall,
    AgentFinishReason,
    AgentLlmMessageDelta,
    AgentMcpToolCallInfo,
)


class ThinkingBlock(pydantic.BaseModel):
    """Folded thinking block — open until ``signature`` arrives, then closed."""

    type: typing.Literal["thinking"] = "thinking"
    thinking: str = ""
    signature: typing.Optional[str] = None


class RedactedThinkingBlock(pydantic.BaseModel):
    type: typing.Literal["redacted_thinking"] = "redacted_thinking"
    data: str


ThinkingBlockUnion = typing.Union[ThinkingBlock, RedactedThinkingBlock]


class ToolCallFunction(pydantic.BaseModel):
    name: str = ""
    arguments: str = ""


class EnrichedToolCall(pydantic.BaseModel):
    """One tool call slot, accumulated by stream ``index``. Mirrors the gateway's ``EnrichedToolCall``."""

    id: str = ""
    type: typing.Literal["function"] = "function"
    function: ToolCallFunction = pydantic.Field(default_factory=ToolCallFunction)
    tool_info: typing.Optional[AgentMcpToolCallInfo] = pydantic.Field(
        default=None,
        description="First chunk with tool_info wins; later chunks do not overwrite.",
    )
    provider_specific_fields: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(
        default=None,
        description="First chunk with provider_specific_fields wins; later chunks do not overwrite.",
    )

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)


class EnrichedAssistantMessage(pydantic.BaseModel):
    """Accumulated assistant message for one turn (until ``finish_reason``).

    Mirrors the gateway's ``EnrichedAssistantMessage`` (``src/agent/LLMTypes.ts``):
    ``tool_calls`` carry ``tool_info``, unlike the leaner ``RawAssistantMessage``.
    """

    type: typing.Literal["agent.message"] = "agent.message"
    role: typing.Literal["assistant"] = "assistant"
    execution_id: str
    content: typing.Optional[str] = None
    refusal: typing.Optional[str] = pydantic.Field(
        default=None,
        description="Concatenated across chunks (gateway does not fold this yet).",
    )
    thinking_blocks: typing.Optional[typing.List[ThinkingBlockUnion]] = None
    tool_calls: typing.Optional[typing.List[EnrichedToolCall]] = None
    finish_reason: typing.Optional[AgentFinishReason] = pydantic.Field(
        default=None,
        description="Set from the chunk that carries finish_reason; may arrive without content.",
    )
    created_at: typing.Optional[float] = pydantic.Field(
        default=None,
        description="Not populated by merge_assistant_message.",
    )

    model_config = pydantic.ConfigDict(extra="allow", arbitrary_types_allowed=True)


def is_assistant_delta(event: typing.Any) -> bool:
    """True for assistant streaming deltas — ``agent.message`` that is not a tool result."""
    return getattr(event, "type", None) == "agent.message" and getattr(event, "role", None) != "tool"


def merge_assistant_message(
    current: typing.Optional[EnrichedAssistantMessage],
    chunk: AgentLlmMessageDelta,
) -> EnrichedAssistantMessage:
    """
    Merge one assistant delta into rolling state.

    Args:
        current: Accumulated message so far, or ``None`` to start a new turn.
        chunk: A single ``agent.message`` assistant delta from the SSE stream.

    Returns:
        Updated message. Does not reset on ``finish_reason`` — caller clears ``current``.
    """
    m = (
        current.model_copy(deep=True)
        if current
        else EnrichedAssistantMessage(execution_id=getattr(chunk, "execution_id", ""))
    )

    content = getattr(chunk, "content", None)
    if content:
        m.content = (m.content or "") + content

    refusal = getattr(chunk, "refusal", None)
    if refusal:
        m.refusal = (m.refusal or "") + refusal

    thinking_blocks = getattr(chunk, "thinking_blocks", None)
    if thinking_blocks:
        m.thinking_blocks = _fold_thinking(m.thinking_blocks or [], thinking_blocks)

    tool_calls = getattr(chunk, "tool_calls", None)
    if tool_calls:
        m.tool_calls = _fold_tool_calls(m.tool_calls or [], tool_calls)

    finish_reason = getattr(chunk, "finish_reason", None)
    if finish_reason is not None:
        m.finish_reason = finish_reason

    return m


def _fold_thinking(
    acc: typing.List[ThinkingBlockUnion],
    incoming: typing.Sequence[typing.Any],
) -> typing.List[ThinkingBlockUnion]:
    for b in incoming:
        if getattr(b, "type", None) == "thinking":
            thinking_text = getattr(b, "thinking", "") or ""
            signature = getattr(b, "signature", None)
            last = acc[-1] if acc else None
            if isinstance(last, ThinkingBlock) and not last.signature:
                last.thinking += thinking_text
                if signature:
                    last.signature = signature
            else:
                acc.append(ThinkingBlock(thinking=thinking_text, signature=signature))
        else:
            acc.append(RedactedThinkingBlock(data=getattr(b, "data", "")))
    return acc


def _fold_tool_calls(
    acc: typing.List[EnrichedToolCall],
    incoming: typing.Sequence[AgentExtendedDeltaToolCall],
) -> typing.List[EnrichedToolCall]:
    for d in incoming:
        index = getattr(d, "index", 0) or 0
        while len(acc) <= index:
            acc.append(EnrichedToolCall())
        tc = acc[index]
        d_id = getattr(d, "id", None)
        if d_id:
            tc.id = d_id
        d_fn = getattr(d, "function", None)
        if d_fn is not None:
            fn_name = getattr(d_fn, "name", None)
            if fn_name:
                tc.function.name = fn_name
            fn_args = getattr(d_fn, "arguments", None)
            if fn_args:
                tc.function.arguments += fn_args
        d_tool_info = getattr(d, "tool_info", None)
        if d_tool_info is not None and tc.tool_info is None:
            tc.tool_info = d_tool_info
        d_psf = getattr(d, "provider_specific_fields", None)
        if d_psf and tc.provider_specific_fields is None:
            tc.provider_specific_fields = dict(d_psf)
    return acc
