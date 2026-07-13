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
    sequence_number : typing.Optional[int]
        SSE event id for resume; None if unavailable from the stream.
    event : TurnStreamingEvent
        Streaming event payload.
    """

    # Sequence number from the SSE event id. None when not available from the underlying stream.
    sequence_number: typing.Optional[int]
    event: TurnStreamingEvent
