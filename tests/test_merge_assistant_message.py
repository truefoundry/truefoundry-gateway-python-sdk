"""Unit tests for merge_assistant_message (mirrors gateway accumulateTokensFromChunk)."""

from __future__ import annotations

from typing import Any, Optional

from truefoundry_gateway_sdk import (
    AgentExtendedDeltaToolCall,
    AgentLlmMessageDelta,
    AgentMcpToolCallInfo,
    AgentRedactedThinkingBlock,
    AgentThinkingBlock,
)
from truefoundry_gateway_sdk.helpers import (
    EnrichedAssistantMessage,
    ThinkingBlock,
    is_assistant_delta,
    merge_assistant_message,
)
from truefoundry_gateway_sdk.types.chat_completion_chunk_delta_tool_call import (
    ChatCompletionChunkDeltaToolCallFunction,
)

EXEC = "exec_1"
PARENT = "49098506-0137-41e1-9017-88804bf81fad"
CHILD = "3786add1-fa41-4124-aaa9-30861eb6eb3b"


def d(execution_id: str = EXEC, **kwargs: Any) -> AgentLlmMessageDelta:
    kwargs.setdefault("role", "assistant")
    return AgentLlmMessageDelta(type="agent.message", execution_id=execution_id, **kwargs)


def fold(chunks: list[AgentLlmMessageDelta]) -> EnrichedAssistantMessage:
    cur: Optional[EnrichedAssistantMessage] = None
    for c in chunks:
        cur = merge_assistant_message(cur, c)
    assert cur is not None
    return cur


def fold_turns(chunks: list[AgentLlmMessageDelta]) -> list[EnrichedAssistantMessage]:
    turns: list[EnrichedAssistantMessage] = []
    cur: Optional[EnrichedAssistantMessage] = None
    for chunk in chunks:
        cur = merge_assistant_message(cur, chunk)
        if cur.finish_reason is not None:
            turns.append(cur)
            cur = None
    return turns


def test_is_assistant_delta() -> None:
    assert is_assistant_delta(d()) is True
    assert is_assistant_delta(AgentLlmMessageDelta(type="agent.message", execution_id=EXEC)) is True

    class ToolMsg:
        type = "agent.message"
        role = "tool"

    assert is_assistant_delta(ToolMsg()) is False
    for t in ("response.created", "mcp.initialize", "agent.done", "response.done"):

        class E:
            pass

        e = E()
        e.type = t  # type: ignore[attr-defined]
        assert is_assistant_delta(e) is False


def test_content_finish_reason_and_reasoning() -> None:
    merged = fold(
        [
            d(reasoning_content="plan the tool call"),
            d(content="Both approaches returned the same result. "),
            d(content="Here's a side-by-side comparison."),
            d(finish_reason="stop"),
        ]
    )
    assert merged.content == "Both approaches returned the same result. Here's a side-by-side comparison."
    assert merged.finish_reason == "stop"
    assert not hasattr(merged, "reasoning_content")


def test_thinking_blocks() -> None:
    multi = fold(
        [
            d(thinking_blocks=[AgentThinkingBlock(type="thinking", thinking="The user wants details via the sandbox, ")]),
            d(thinking_blocks=[AgentThinkingBlock(type="thinking", thinking="using the mcp-client tool.")]),
            d(thinking_blocks=[AgentThinkingBlock(type="thinking", thinking="", signature="sig_1")]),
            d(thinking_blocks=[AgentThinkingBlock(type="thinking", thinking="Summarize for the user.")]),
        ]
    )
    blocks = multi.thinking_blocks or []
    assert len(blocks) == 2
    first = blocks[0]
    assert isinstance(first, ThinkingBlock)
    assert first.thinking == "The user wants details via the sandbox, using the mcp-client tool."
    assert first.signature == "sig_1"

    redacted = fold([d(thinking_blocks=[AgentRedactedThinkingBlock(type="redacted_thinking", data="blob")])])
    assert (redacted.thinking_blocks or [])[0].type == "redacted_thinking"


def test_tool_calls() -> None:
    merged = fold(
        [
            d(
                tool_calls=[
                    AgentExtendedDeltaToolCall(
                        index=0,
                        id="toolu_0",
                        type="function",
                        function=ChatCompletionChunkDeltaToolCallFunction(name="exec", arguments='{"intent": '),
                    )
                ]
            ),
            d(
                tool_calls=[
                    AgentExtendedDeltaToolCall(
                        index=0,
                        function=ChatCompletionChunkDeltaToolCallFunction(arguments='"Get user details", '),
                    )
                ]
            ),
            d(
                tool_calls=[
                    AgentExtendedDeltaToolCall(
                        index=0,
                        function=ChatCompletionChunkDeltaToolCallFunction(arguments='"command": "mcp-client get_me {}"}'),
                    )
                ]
            ),
            d(
                tool_calls=[
                    AgentExtendedDeltaToolCall(
                        index=0,
                        tool_info=AgentMcpToolCallInfo(
                            mcp_server_id="sandbox",
                            mcp_server_name="sandbox",
                            original_tool_name="exec",
                        ),
                    )
                ]
            ),
            d(finish_reason="tool_calls"),
        ]
    )
    assert merged.tool_calls is not None
    assert merged.tool_calls[0].function.arguments == '{"intent": "Get user details", "command": "mcp-client get_me {}"}'
    assert merged.tool_calls[0].tool_info is not None
    assert merged.tool_calls[0].tool_info.mcp_server_name == "sandbox"
    assert merged.finish_reason == "tool_calls"

    padded = fold(
        [
            d(
                tool_calls=[
                    AgentExtendedDeltaToolCall(
                        index=1,
                        id="toolu_1",
                        function=ChatCompletionChunkDeltaToolCallFunction(name="exec", arguments="{}"),
                    )
                ]
            )
        ]
    )
    calls = padded.tool_calls or []
    assert len(calls) == 2
    assert calls[0].id == ""
    assert calls[1].id == "toolu_1"


def test_caller_patterns() -> None:
    turns = fold_turns(
        [
            d(
                tool_calls=[
                    AgentExtendedDeltaToolCall(
                        index=0,
                        id="toolu_0",
                        function=ChatCompletionChunkDeltaToolCallFunction(name="exec", arguments='{"cmd":'),
                    )
                ]
            ),
            d(
                tool_calls=[
                    AgentExtendedDeltaToolCall(
                        index=0,
                        function=ChatCompletionChunkDeltaToolCallFunction(arguments='"ls"}'),
                    )
                ]
            ),
            d(finish_reason="tool_calls"),
            d(content="Done."),
            d(finish_reason="stop"),
        ]
    )
    assert len(turns) == 2
    assert turns[0].tool_calls is not None
    assert turns[0].tool_calls[0].function.arguments == '{"cmd":"ls"}'
    assert turns[1].content == "Done."

    by_exec: dict[str, Optional[EnrichedAssistantMessage]] = {}
    for chunk in [
        d(content="Parent ", execution_id=PARENT),
        d(content="Child ", execution_id=CHILD),
        d(content="turn.", execution_id=PARENT),
        d(content="turn.", execution_id=CHILD),
    ]:
        by_exec[chunk.execution_id] = merge_assistant_message(by_exec.get(chunk.execution_id), chunk)
    parent_msg = by_exec[PARENT]
    child_msg = by_exec[CHILD]
    assert parent_msg is not None
    assert child_msg is not None
    assert parent_msg.content == "Parent turn."
    assert child_msg.content == "Child turn."


def _event(type: str, **kwargs: Any) -> Any:
    class E:
        pass

    e = E()
    setattr(e, "type", type)
    for k, v in kwargs.items():
        setattr(e, k, v)
    return e


def _replay_stream(events: list[Any]) -> list[EnrichedAssistantMessage]:
    """Filter non-assistant events, merge deltas, snapshot on finish_reason."""
    turns: list[EnrichedAssistantMessage] = []
    cur: Optional[EnrichedAssistantMessage] = None
    for ev in events:
        if not is_assistant_delta(ev):
            continue
        cur = merge_assistant_message(cur, ev)
        if cur.finish_reason is not None:
            turns.append(cur)
            cur = None
    return turns


def test_replay_mixed_stream() -> None:
    thinking = "The user wants details via the sandbox, using the mcp-client tool. Let me run both approaches."
    turns = _replay_stream(
        [
            _event("response.created", response_id="g.test"),
            d(reasoning_content=thinking),
            d(
                tool_calls=[
                    AgentExtendedDeltaToolCall(
                        index=0,
                        id="toolu_0",
                        type="function",
                        function=ChatCompletionChunkDeltaToolCallFunction(
                            name="exec", arguments='{"intent": "Get user details", '
                        ),
                        tool_info=AgentMcpToolCallInfo(
                            mcp_server_id="sandbox",
                            mcp_server_name="sandbox",
                            original_tool_name="exec",
                        ),
                    )
                ]
            ),
            d(
                tool_calls=[
                    AgentExtendedDeltaToolCall(
                        index=0,
                        function=ChatCompletionChunkDeltaToolCallFunction(arguments='"command": "mcp-client get_me {}"}'),
                    )
                ]
            ),
            d(
                thinking_blocks=[AgentThinkingBlock(type="thinking", thinking=thinking, signature="sig_a")],
                finish_reason="tool_calls",
            ),
            _event("agent.message", role="tool", execution_id=EXEC, tool_call_id="toolu_0", content='{"success":true}'),
            d(content="Both approaches returned the same result. "),
            d(content="Here's a side-by-side comparison."),
            d(finish_reason="stop"),
            _event("response.done", status="done"),
        ]
    )

    assert len(turns) == 2
    assert turns[0].tool_calls is not None
    assert turns[0].tool_calls[0].function.arguments == '{"intent": "Get user details", "command": "mcp-client get_me {}"}'
    assert turns[0].tool_calls[0].tool_info is not None
    assert turns[0].tool_calls[0].tool_info.mcp_server_name == "sandbox"
    assert turns[0].thinking_blocks is not None
    first_thinking = turns[0].thinking_blocks[0]
    assert isinstance(first_thinking, ThinkingBlock)
    assert first_thinking.thinking == thinking
    assert turns[0].finish_reason == "tool_calls"
    assert turns[0].content is None
    assert turns[1].content == "Both approaches returned the same result. Here's a side-by-side comparison."
    assert turns[1].finish_reason == "stop"
