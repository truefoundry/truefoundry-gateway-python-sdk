from __future__ import annotations

import logging
import typing
from json.decoder import JSONDecodeError

import httpx
from ..core.http_sse._api import EventSource
from ..core.pydantic_utilities import parse_sse_obj
from ..types.turn_streaming_event import TurnStreamingEvent
from .turn_stream_data import TurnStreamData

_logger = logging.getLogger(__name__)


def parse_sequence_number(sse_id: str) -> int:
    """Parse the SSE ``id`` field as a sequence number.

    Raises ``ValueError`` when the id is absent or not a valid integer —
    mirroring the TypeScript ``parseSequenceNumber`` which throws in the same cases.
    """
    if not sse_id:
        raise ValueError("Missing SSE sequence number id.")
    try:
        return int(sse_id)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid SSE sequence number id: {sse_id!r}.")


def iter_sse_stream(response: httpx.Response) -> typing.Iterator[TurnStreamData]:
    """Iterate a live httpx SSE response, yielding parsed :class:`TurnStreamData` items.

    Skips unparseable events (with a warning) rather than raising, mirroring the
    behaviour of the generated raw client. Raises on a missing or malformed SSE
    ``id`` field via :func:`parse_sequence_number`.
    """
    for _sse in EventSource(response).iter_sse():
        if not _sse.data:
            continue
        try:
            event = typing.cast(
                TurnStreamingEvent,
                parse_sse_obj(sse=_sse, type_=TurnStreamingEvent),  # type: ignore[arg-type]
            )
        except JSONDecodeError as e:
            _logger.warning("Skipping SSE event with invalid JSON: %s, sse: %r", e, _sse)
            continue
        except (TypeError, ValueError, KeyError, AttributeError) as e:
            _logger.warning(
                "Skipping SSE event due to model construction error: %s: %s, sse: %r",
                type(e).__name__, e, _sse,
            )
            continue
        except Exception as e:
            _logger.error(
                "Unexpected error processing SSE event: %s: %s, sse: %r",
                type(e).__name__, e, _sse,
            )
            continue
        yield TurnStreamData(sequence_number=parse_sequence_number(_sse.id), event=event)


async def aiter_sse_stream(response: httpx.Response) -> typing.AsyncIterator[TurnStreamData]:
    """Async version of :func:`iter_sse_stream`."""
    async for _sse in EventSource(response).aiter_sse():
        if not _sse.data:
            continue
        try:
            event = typing.cast(
                TurnStreamingEvent,
                parse_sse_obj(sse=_sse, type_=TurnStreamingEvent),  # type: ignore[arg-type]
            )
        except JSONDecodeError as e:
            _logger.warning("Skipping SSE event with invalid JSON: %s, sse: %r", e, _sse)
            continue
        except (TypeError, ValueError, KeyError, AttributeError) as e:
            _logger.warning(
                "Skipping SSE event due to model construction error: %s: %s, sse: %r",
                type(e).__name__, e, _sse,
            )
            continue
        except Exception as e:
            _logger.error(
                "Unexpected error processing SSE event: %s: %s, sse: %r",
                type(e).__name__, e, _sse,
            )
            continue
        yield TurnStreamData(sequence_number=parse_sequence_number(_sse.id), event=event)
