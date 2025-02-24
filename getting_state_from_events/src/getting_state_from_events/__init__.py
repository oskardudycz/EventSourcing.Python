from decimal import Decimal
from typing import Literal, ClassVar
from pydantic import BaseModel
from datetime import datetime
from enum import StrEnum


class ShoppingCartStatus(StrEnum):
    Pending = "Pending"
    Confirmed = "Confirmed"
    Canceled = "Canceled"


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


def handle_shopping_cart_opened(
    event: ShoppingCartOpened, _: ShoppingCart
) -> ShoppingCart:
    return ShoppingCart(
        id=event.data.shopping_cart_id,
        client_id=event.data.client_id,
        status=ShoppingCartStatus.Pending,
        product_items=[],
        opened_at=event.data.opened_at,
    )


def handle_product_item_added(
    event: ProductItemAddedToShoppingCart, state: ShoppingCart
) -> ShoppingCart:
    """
    Handles the ProductItemAddedToShoppingCart event.
    """
    # Add the new product item
    product_items = list(state.product_items)
    product_items.append(event.data.product_item)

    # Group items by productId and unitPrice
    grouped_items: dict[str, list[PricedProductItem]] = {}
    for item in product_items:
        key = f"{item.product_id}_{item.unit_price}"
        if key not in grouped_items:
            grouped_items[key] = []
        grouped_items[key].append(item)

    # Transform groups into final format
    processed_items = [
        PricedProductItem(
            product_id=items[0].product_id,
            quantity=sum(item.quantity for item in items),
            unit_price=items[0].unit_price,
        )
        for items in grouped_items.values()
    ]

    # Return new state with updated product items, excluding product_items from the dump
    state_dict = state.model_dump(exclude={"product_items"})
    return ShoppingCart(**state_dict, product_items=processed_items)


def handle_product_item_removed(
    event: ProductItemRemovedFromShoppingCart, state: ShoppingCart
) -> ShoppingCart:
    """
    Handles removing items by product ID and unit price, updating quantities appropriately.
    """
    # Find matching item and update quantity
    updated_items = []
    removed_item = event.data.product_item

    for item in state.product_items:
        if (
            item.product_id == removed_item.product_id
            and item.unit_price == removed_item.unit_price
        ):
            new_quantity = item.quantity - removed_item.quantity
            if new_quantity > 0:
                updated_items.append(
                    PricedProductItem(
                        product_id=item.product_id,
                        quantity=new_quantity,
                        unit_price=item.unit_price,
                    )
                )
        else:
            updated_items.append(item)

    return ShoppingCart(
        **state.model_dump(exclude={"product_items"}), product_items=updated_items
    )


def handle_shopping_cart_confirmed(
    event: ShoppingCartConfirmed, state: ShoppingCart
) -> ShoppingCart:
    return ShoppingCart(
        **state.model_dump(exclude={"confirmed_at"}),
        confirmed_at=event.data.confirmed_at,
    )


def handle_shopping_cart_canceled(
    event: ShoppingCartCanceled, state: ShoppingCart
) -> ShoppingCart:
    return ShoppingCart(
        **state.model_dump(exclude={"canceled_at"}), canceled_at=event.data.canceled_at
    )


# Event handler mapping
EVENT_HANDLERS = {
    ShoppingCartOpened.type: handle_shopping_cart_opened,
    ProductItemAddedToShoppingCart.type: handle_product_item_added,
    ProductItemRemovedFromShoppingCart.type: handle_product_item_removed,
    ShoppingCartConfirmed.type: handle_shopping_cart_confirmed,
    ShoppingCartCanceled.type: handle_shopping_cart_canceled,
}


def evolve(event: Event, state: ShoppingCart) -> ShoppingCart:
    handler = EVENT_HANDLERS.get(event.type)
    if handler is None:
        raise ValueError(f"Unhandled event type: {event.type}")
    return handler(event, state)  # type: ignore


def get_shopping_cart_from_events(events: list[ShoppingCartEvent]) -> ShoppingCart:
    state = ShoppingCart()
    for event in events:
        state = evolve(event, state)
    return state
