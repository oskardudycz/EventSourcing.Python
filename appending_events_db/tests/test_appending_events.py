from decimal import Decimal
from uuid import uuid4 as uuid
from datetime import datetime, UTC


from appending_events_db.src.appending_events_db import (
    ProductItemRemovedFromShoppingCart,
    ShoppingCartCanceled,
    ShoppingCartConfirmed,
    PricedProductItem,
    ShoppingCartEvent,
    ShoppingCartOpened,
    ProductItemAddedToShoppingCart,
    append_to_stream,
    read_stream,
)
from appending_events_db.src.appending_events_db.event_store import EventStore


def test_should_append_events_to_db(event_store: EventStore) -> None:
    """
    Test that the event types are defined correctly.
    """
    shopping_cart_id = str(uuid())
    client_id = str(uuid())
    pair_of_socks = PricedProductItem(
        product_id=str(uuid()), quantity=2, unit_price=Decimal("10.0")
    )
    current_time = datetime.now(UTC)

    events: list[ShoppingCartEvent] = [
        ShoppingCartOpened(
            data=ShoppingCartOpened.Data(
                shopping_cart_id=shopping_cart_id,
                client_id=client_id,
                opened_at=current_time,
            )
        ),
        ProductItemAddedToShoppingCart(
            data=ProductItemAddedToShoppingCart.Data(
                shopping_cart_id=shopping_cart_id, product_item=pair_of_socks
            )
        ),
        ProductItemRemovedFromShoppingCart(
            data=ProductItemRemovedFromShoppingCart.Data(
                shopping_cart_id=shopping_cart_id, product_item=pair_of_socks
            )
        ),
        ShoppingCartConfirmed(
            data=ShoppingCartConfirmed.Data(
                shopping_cart_id=shopping_cart_id, confirmed_at=current_time
            )
        ),
        ShoppingCartCanceled(
            data=ShoppingCartCanceled.Data(
                shopping_cart_id=shopping_cart_id, canceled_at=current_time
            )
        ),
    ]
    stream_name = f"shopping_cart_{shopping_cart_id}"
    append_to_stream(event_store, stream_name, events)
    events_from_db = read_stream(event_store, stream_name)
    assert events == events_from_db
