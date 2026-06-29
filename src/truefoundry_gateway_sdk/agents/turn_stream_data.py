import dataclasses
import typing

from ..types.turn_streaming_event import TurnStreamingEvent


@dataclasses.dataclass
class TurnStreamData:
    # Sequence number from the SSE event id. None when not available from the underlying stream.
    sequence_number: typing.Optional[int]
    event: TurnStreamingEvent
