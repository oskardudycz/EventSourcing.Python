from decimal import Decimal
from typing import Literal, ClassVar
from pydantic import BaseModel
from datetime import datetime
from enum import StrEnum

from .event_store import EventStore, EventStream
from .model import Event
from typing import Callable


class ShoppingCartStatus(StrEnum):
    Pending = "Pending"
    Confirmed = "Confirmed"
    Canceled = "Canceled"


class ProductItem(BaseModel):
    product_id: str
    quantity: int


class PricedProductItem(ProductItem):
    unit_price: Decimal


class ShoppingCartOpened(Event):
    type: ClassVar[Literal["ShoppingCartOpened"]] = "ShoppingCartOpened"

    class Data(BaseModel):
        shopping_cart_id: str
        client_id: str
        opened_at: datetime

    data: Data


class ProductItemAddedToShoppingCart(Event):
    type: ClassVar[Literal["ProductItemAddedToShoppingCart"]] = (
        "ProductItemAddedToShoppingCart"
    )

    class Data(BaseModel):
        shopping_cart_id: str
        product_item: PricedProductItem

    data: Data


class ProductItemRemovedFromShoppingCart(Event):
    type: ClassVar[Literal["ProductItemRemovedFromShoppingCart"]] = (
        "ProductItemRemovedFromShoppingCart"
    )

    class Data(BaseModel):
        shopping_cart_id: str
        product_item: PricedProductItem

    data: Data


class ShoppingCartConfirmed(Event):
    type: ClassVar[Literal["ShoppingCartConfirmed"]] = "ShoppingCartConfirmed"

    class Data(BaseModel):
        shopping_cart_id: str
        confirmed_at: datetime

    data: Data


class ShoppingCartCanceled(Event):
    type: ClassVar[Literal["ShoppingCartCanceled"]] = "ShoppingCartCanceled"

    class Data(BaseModel):
        shopping_cart_id: str
        canceled_at: datetime

    data: Data


type ShoppingCartEvent = (
    ShoppingCartOpened
    | ProductItemAddedToShoppingCart
    | ProductItemRemovedFromShoppingCart
    | ShoppingCartConfirmed
    | ShoppingCartCanceled
    | Event
)


class ShoppingCart(BaseModel):
    id: str | None = None
    client_id: str | None = None
    status: ShoppingCartStatus = ShoppingCartStatus.Pending
    product_items: list[PricedProductItem] = []
    opened_at: datetime | None = None
    confirmed_at: datetime | None = None
    canceled_at: datetime | None = None

    class Config:
        frozen = True


def append_to_stream(
    event_store: EventStore, stream_name: str, events: list[ShoppingCartEvent]
) -> None:
    event_store.append_events(stream_name, events)


def read_stream(event_store: EventStore, stream_name: str) -> list[ShoppingCartEvent]:
    events = event_store.read_stream(stream_name)
    event_handlers: dict[str, Callable[[EventStream], ShoppingCartEvent]] = {
        ShoppingCartOpened.type: lambda e: ShoppingCartOpened(
            data=ShoppingCartOpened.Data.model_validate_json(str(e.event_data))
        ),
        ProductItemAddedToShoppingCart.type: lambda e: ProductItemAddedToShoppingCart(
            data=ProductItemAddedToShoppingCart.Data.model_validate_json(
                str(e.event_data)
            )
        ),
        ProductItemRemovedFromShoppingCart.type: lambda e: ProductItemRemovedFromShoppingCart(
            data=ProductItemRemovedFromShoppingCart.Data.model_validate_json(
                str(e.event_data)
            )
        ),
        ShoppingCartConfirmed.type: lambda e: ShoppingCartConfirmed(
            data=ShoppingCartConfirmed.Data.model_validate_json(str(e.event_data))
        ),
        ShoppingCartCanceled.type: lambda e: ShoppingCartCanceled(
            data=ShoppingCartCanceled.Data.model_validate_json(str(e.event_data))
        ),
    }
    return [event_handlers[str(event.event_type)](event) for event in events]
