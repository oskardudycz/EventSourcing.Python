from typing import Literal
from pydantic import BaseModel
from datetime import datetime
from enum import StrEnum


class ShoppingCartStatus(StrEnum):
    Pending = "Pending"
    Confirmed = "Confirmed"
    Canceled = "Canceled"


class Event(BaseModel):
    type: str
    data: BaseModel

    class Config:
        frozen = True


class ProductItem(BaseModel):
    product_id: str
    quantity: int


class PricedProductItem(ProductItem):
    unit_price: float


class ShoppingCartOpened(Event):
    type: Literal["ShoppingCartOpened"] = "ShoppingCartOpened"

    class Data(BaseModel):
        shopping_cart_id: str
        client_id: str
        opened_at: datetime

    data: Data


class ProductItemAddedToShoppingCart(Event):
    type: Literal["ProductItemAddedToShoppingCart"] = "ProductItemAddedToShoppingCart"

    class Data(BaseModel):
        shopping_cart_id: str
        product_item: PricedProductItem

    data: Data


class ProductItemRemovedFromShoppingCart(Event):
    type: Literal["ProductItemRemovedFromShoppingCart"] = (
        "ProductItemRemovedFromShoppingCart"
    )

    class Data(BaseModel):
        shopping_cart_id: str
        product_item: PricedProductItem

    data: Data


class ShoppingCartConfirmed(Event):
    type: Literal["ShoppingCartConfirmed"] = "ShoppingCartConfirmed"

    class Data(BaseModel):
        shopping_cart_id: str
        confirmed_at: datetime

    data: Data


class ShoppingCartCanceled(Event):
    type: Literal["ShoppingCartCanceled"] = "ShoppingCartCanceled"

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


class ShoppingCart(BaseModel):
    id: str
    client_id: str
    status: ShoppingCartStatus
    product_items: list[PricedProductItem]
    opened_at: datetime
    confirmed_at: datetime | None = None
    canceled_at: datetime | None = None

    class Config:
        frozen = True
