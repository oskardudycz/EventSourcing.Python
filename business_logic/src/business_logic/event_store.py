from typing import Generic, TypeVar

T = TypeVar("T")


class EventStore(Generic[T]):
    def __init__(self) -> None:
        self.streams: dict[str, list[T]] = {}

    def read_stream(self, stream_name: str) -> list[T]:
        return self.streams[stream_name]

    def append_events(self, stream_name: str, events: list[T]) -> None:
        if stream_name not in self.streams:
            self.streams[stream_name] = []
        self.streams[stream_name].extend(events)
