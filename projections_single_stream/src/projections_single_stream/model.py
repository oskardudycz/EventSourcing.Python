import uuid
from datetime import datetime
from typing import ClassVar
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Event(BaseModel):
    type: ClassVar[str]

    class Data(BaseModel):
        pass

    data: Data

    model_config = ConfigDict(frozen=True)


class Command(BaseModel):
    type: ClassVar[str]

    class Data(BaseModel):
        pass

    data: Data

    model_config = ConfigDict(frozen=True)
