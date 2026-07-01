import dataclasses
import typing

from ..types.turn_streaming_event import TurnStreamingEvent


@dataclasses.dataclass
class TurnStreamData:
    """An SSE item with a TurnStreamingEvent; ``sequence_number`` is the SSE event id for resuming via ``subscribe_to_turn``."""

    # Sequence number from the SSE event id. None when not available from the underlying stream.
    sequence_number: typing.Optional[int]
    event: TurnStreamingEvent
