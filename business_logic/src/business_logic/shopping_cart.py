from decimal import Decimal
from typing import Literal, ClassVar
from pydantic import BaseModel
from datetime import datetime
from enum import StrEnum
from .core import merge


class Event(BaseModel):
    type: ClassVar[str]
    data: BaseModel

    class Config:
        frozen = True


class ProductItem(BaseModel):
    product_id: str
    quantity: int


class PricedProductItem(ProductItem):
    unit_price: Decimal

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PricedProductItem):
            return False
        return (
            self.product_id == other.product_id and self.unit_price == other.unit_price
        )


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
)


class ShoppingCartStatus(StrEnum):
    Empty = "Empty"
    Pending = "Pending"
    Confirmed = "Confirmed"
    Canceled = "Canceled"


class Empty(BaseModel):
    status: ClassVar[ShoppingCartStatus] = ShoppingCartStatus.Empty


class Pending(BaseModel):
    id: str
    status: ClassVar[ShoppingCartStatus] = ShoppingCartStatus.Pending
    product_items: list[PricedProductItem] = []
    client_id: str
    opened_at: datetime


class Confirmed(BaseModel):
    id: str
    status: ClassVar[ShoppingCartStatus] = ShoppingCartStatus.Confirmed
    confirmed_at: datetime
    product_items: list[PricedProductItem] = []
    client_id: str


class Canceled(BaseModel):
    id: str
    status: ClassVar[ShoppingCartStatus] = ShoppingCartStatus.Canceled
    canceled_at: datetime
    product_items: list[PricedProductItem] = []
    client_id: str


type ShoppingCart = Empty | Pending | Confirmed | Canceled

empty_shopping_cart = Empty()


def apply_shopping_cart_opened(
    event: ShoppingCartOpened, state: ShoppingCart
) -> ShoppingCart:
    return Pending(
        id=event.data.shopping_cart_id,
        product_items=[],
        client_id=event.data.client_id,
        opened_at=event.data.opened_at,
    )


def apply_product_item_added(
    event: ProductItemAddedToShoppingCart, state: ShoppingCart
) -> ShoppingCart:
    if not isinstance(state, Pending):
        return state

    return Pending(
        **state.model_dump(exclude={"product_items"}),
        product_items=merge(
            state.product_items,
            event.data.product_item,
            lambda p: p.product_id == event.data.product_item.product_id
            and p.unit_price == event.data.product_item.unit_price,
            lambda p, _: PricedProductItem(
                product_id=p.product_id,
                quantity=p.quantity + event.data.product_item.quantity,
                unit_price=p.unit_price,
            ),
            on_not_found=lambda _: event.data.product_item,
        ),
    )


def apply_product_item_removed(
    event: ProductItemRemovedFromShoppingCart, state: ShoppingCart
) -> ShoppingCart:
    if not isinstance(state, Pending):
        return state

    return Pending(
        **state.model_dump(exclude={"product_items"}),
        product_items=merge(
            state.product_items,
            event.data.product_item,
            lambda p: p.product_id == event.data.product_item.product_id
            and p.unit_price == event.data.product_item.unit_price,
            lambda p, _: PricedProductItem(
                product_id=p.product_id,
                quantity=p.quantity - event.data.product_item.quantity,
                unit_price=p.unit_price,
            ),
            on_not_found=lambda _: None,
        ),
    )


def apply_shopping_cart_confirmed(
    event: ShoppingCartConfirmed, state: ShoppingCart
) -> ShoppingCart:
    if not isinstance(state, Pending):
        return state

    return Confirmed(
        **state.model_dump(),
        confirmed_at=event.data.confirmed_at,
    )


def apply_shopping_cart_canceled(
    event: ShoppingCartCanceled, state: ShoppingCart
) -> ShoppingCart:
    if not isinstance(state, Pending):
        return state

    return Canceled(
        **state.model_dump(),
        canceled_at=event.data.canceled_at,
    )


def evolve(event: ShoppingCartEvent, state: ShoppingCart) -> ShoppingCart:
    match event:
        case ShoppingCartOpened():
            return apply_shopping_cart_opened(event, state)
        case ProductItemAddedToShoppingCart():
            return apply_product_item_added(event, state)
        case ProductItemRemovedFromShoppingCart():
            return apply_product_item_removed(event, state)
        case ShoppingCartConfirmed():
            return apply_shopping_cart_confirmed(event, state)
        case ShoppingCartCanceled():
            return apply_shopping_cart_canceled(event, state)
        case _:
            raise ValueError(f"Unhandled event type: {event.type}")


def get_shopping_cart_from_events(events: list[ShoppingCartEvent]) -> ShoppingCart:
    state: ShoppingCart = Empty()
    for event in events:
        state = evolve(event, state)
    return state
