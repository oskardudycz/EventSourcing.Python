from decimal import Decimal
from typing import Literal, ClassVar
from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(frozen=True)


def apply_shopping_cart_opened(
    event: ShoppingCartOpened, _: ShoppingCart
) -> ShoppingCart:
    return ShoppingCart(
        id=event.data.shopping_cart_id,
        client_id=event.data.client_id,
        status=ShoppingCartStatus.Pending,
        product_items=[],
        opened_at=event.data.opened_at,
    )


def apply_product_item_added(
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


def apply_product_item_removed(
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


def apply_shopping_cart_confirmed(
    event: ShoppingCartConfirmed, state: ShoppingCart
) -> ShoppingCart:
    return ShoppingCart(
        **state.model_dump(exclude={"confirmed_at"}),
        confirmed_at=event.data.confirmed_at,
    )


def apply_shopping_cart_canceled(
    event: ShoppingCartCanceled, state: ShoppingCart
) -> ShoppingCart:
    return ShoppingCart(
        **state.model_dump(exclude={"canceled_at"}), canceled_at=event.data.canceled_at
    )


def evolve(event: Event, state: ShoppingCart) -> ShoppingCart:
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
    state = ShoppingCart()
    for event in events:
        state = evolve(event, state)
    return state


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
