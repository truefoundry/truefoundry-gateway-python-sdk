from __future__ import annotations

import dataclasses
import typing

if typing.TYPE_CHECKING:
    from ..types.turn_streaming_event import TurnStreamingEvent


@dataclasses.dataclass
class TurnStreamData:
    """
    Attributes
    ----------
    sequence_number : int
        SSE event id used for resume via ``subscribe_to_turn``.
    event : TurnStreamingEvent
        Streaming event payload.
    """

    sequence_number: int
    event: TurnStreamingEvent
