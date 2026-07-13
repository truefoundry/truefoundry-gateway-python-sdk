from __future__ import annotations

import typing

from ..core.pydantic_utilities import IS_PYDANTIC_V2
from ..types.chat_completion_content_part_text import ChatCompletionContentPartText
from ..types.chat_completion_message_tool_call_function import ChatCompletionMessageToolCallFunction
from ..types.model_message_delta_event import ModelMessageDeltaEvent
from ..types.model_message_event import ModelMessageEvent
from ..types.tool_call import ToolCall

if typing.TYPE_CHECKING:
    from ..types.turn_event import TurnEvent
    from ..types.turn_streaming_event import TurnStreamingEvent

# Union of all streaming delta events. Expand as more `.delta` events are added.
DeltaEvents = ModelMessageDeltaEvent


def is_event_delta(event: TurnStreamingEvent) -> bool:
    """
    True for ``.delta`` streaming events.

    Parameters
    ----------
    event : TurnStreamingEvent
        Streaming event to check for delta type.

    Returns
    -------
    bool
        True if the event is a delta chunk.
    """
    return event.type.endswith(".delta")


def merge_event_delta(base: TurnEvent, delta: DeltaEvents) -> None:
    """
    Merge ``delta`` into ``base`` in place (same ``id`` required).

    Parameters
    ----------
    base : TurnEvent
        Base event to merge delta chunks into.
    delta : DeltaEvents
        Delta chunk to merge into the base event.

    Returns
    -------
    None
        Updates ``base`` in place.
    """
    if base.id != delta.id:
        raise ValueError(f'Cannot merge delta into a different event: base id "{base.id}" != delta id "{delta.id}".')
    if isinstance(delta, ModelMessageDeltaEvent) and isinstance(base, ModelMessageEvent):
        _merge_model_message_delta(base, delta)


def _merge_model_message_delta(base: ModelMessageEvent, delta: ModelMessageDeltaEvent) -> None:
    if delta.content:
        if base.content is None or isinstance(base.content, str):
            base.content = (base.content or "") + delta.content
        else:
            last = base.content[-1] if base.content else None
            if last is not None and last.type == "text":
                last.text += delta.content  # type: ignore[union-attr]
            else:
                base.content.append(ChatCompletionContentPartText(type="text", text=delta.content))

    if delta.refusal:
        base.refusal = (base.refusal or "") + delta.refusal

    if delta.tool_calls:
        if base.tool_calls is None:
            base.tool_calls = []
        for d in delta.tool_calls:
            while len(base.tool_calls) <= d.index:
                base.tool_calls.append(typing.cast(ToolCall, None))
            tc: typing.Optional[ToolCall] = base.tool_calls[d.index]
            if tc is None:
                fn = ChatCompletionMessageToolCallFunction(
                    name=d.function.name if d.function and d.function.name else "",
                    arguments="",
                )
                construct_kwargs: typing.Dict[str, typing.Any] = dict(
                    id=d.id or "",
                    type=d.type or "function",
                    function=fn,
                    tool_info=d.tool_info,
                    provider_specific_fields=None,
                )
                if IS_PYDANTIC_V2:
                    tc = ToolCall.model_construct(**construct_kwargs)
                else:
                    tc = ToolCall.construct(**construct_kwargs)
                base.tool_calls[d.index] = tc
            if d.id:
                tc.id = d.id
            if d.type:
                tc.type = d.type  # type: ignore[assignment]
            if d.function and d.function.name:
                tc.function.name = d.function.name
            if d.function and d.function.arguments:
                tc.function.arguments = (tc.function.arguments or "") + d.function.arguments
            if d.tool_info:
                tc.tool_info = d.tool_info  # type: ignore[assignment]
            if d.provider_specific_fields:
                tc.provider_specific_fields = {  # type: ignore[assignment]
                    **(tc.provider_specific_fields or {}),
                    **d.provider_specific_fields,
                }

    if delta.finish_reason:
        base.finish_reason = delta.finish_reason

    if delta.reasoning_content:
        base.reasoning_content = (base.reasoning_content or "") + delta.reasoning_content

    if delta.usage:
        base.usage = delta.usage
