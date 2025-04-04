from typing import Generic, TypeVar, Callable, Protocol, cast
from collections import defaultdict
from uuid import uuid4
from pydantic import BaseModel
from projections_single_stream.src.projections_single_stream.model import Event


class EventMetadata(BaseModel):
    event_id: str
    stream_position: int
    log_position: int


class EventEnvelope(Event):
    metadata: EventMetadata


type EventHandler = Callable[[EventEnvelope], None]


class EventWithTypeAndData(Protocol):
    """Protocol that defines the expected structure of events."""

    @property
    def type(self) -> str: ...
    @property
    def data(self) -> BaseModel: ...


T = TypeVar("T", bound=EventWithTypeAndData)


class EventStore(Generic[T]):
    def __init__(self) -> None:
        self.streams: dict[str, list[T]] = defaultdict(list)
        self.handlers: list[EventHandler] = []

    def read_stream(self, stream_name: str) -> list[T]:
        return self.streams[stream_name]

    def append_events(self, stream_name: str, events: list[T]) -> None:
        current_stream = self.streams.get(stream_name, [])

        event_envelopes: list[EventEnvelope] = []
        for index, event in enumerate(events):
            # Create metadata for the event
            metadata = EventMetadata(
                event_id=str(uuid4()),
                stream_position=len(current_stream) + index + 1,
                log_position=0,
            )

            # We need to cast the event data to the expected Event.Data type
            # This is safe because the Event envelope's data will have the same structure
            data = cast(Event.Data, event.data)

            # Create the event envelope
            envelope = EventEnvelope(
                data=data,
                metadata=metadata,
            )

            # Set the type using object.__setattr__ to bypass frozen=True
            object.__setattr__(envelope, "type", event.type)
            event_envelopes.append(envelope)

        for event_envelope in event_envelopes:
            for handler in self.handlers:
                handler(event_envelope)

    def subscribe(self, event_handler: EventHandler) -> None:
        self.handlers.append(event_handler)
