from sqlalchemy.orm import Session
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from .model import Event, Base
import uuid
from sqlalchemy.orm import Mapped, mapped_column


class EventStream(Base):
    __tablename__ = "event_streams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )
    stream_name = Column(String, nullable=False)
    event_data = Column(JSONB, nullable=False)
    event_type = Column(String, nullable=False)


class EventStore:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def append_events(self, stream_name: str, events: list[Event]) -> None:
        with self.db_session.begin():
            for event in events:
                self.db_session.add(
                    EventStream(
                        stream_name=stream_name,
                        event_type=event.type,
                        event_data=event.data.model_dump_json(),
                    )
                )

    def read_stream(self, stream_name: str) -> list[EventStream]:
        return (
            self.db_session.query(EventStream)
            .filter(EventStream.stream_name == stream_name)
            .all()
        )
