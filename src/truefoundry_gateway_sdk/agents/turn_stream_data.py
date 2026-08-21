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


def parse_sequence_number(sse_id: typing.Optional[str]) -> int:
    """Parse the SSE ``id`` field as a sequence number.

    Raises ``ValueError`` when the id is absent or not a valid integer —
    mirroring the TypeScript ``parseSequenceNumber``.
    """
    if not sse_id:
        raise ValueError("Missing SSE sequence number id.")
    try:
        return int(sse_id)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid SSE sequence number id: {sse_id!r}.") from exc
