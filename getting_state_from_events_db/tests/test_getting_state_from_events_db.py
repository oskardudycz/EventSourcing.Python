from decimal import Decimal
from uuid import uuid4 as uuid
from datetime import datetime, UTC


from getting_state_from_events_db.src.getting_state_from_events_db import (
    ProductItemRemovedFromShoppingCart,
    ShoppingCartCanceled,
    ShoppingCartConfirmed,
    PricedProductItem,
    ShoppingCartEvent,
    ShoppingCartOpened,
    ProductItemAddedToShoppingCart,
    ShoppingCartStatus,
    append_to_stream,
    read_stream,
    get_shopping_cart_from_events,
)
from getting_state_from_events_db.src.getting_state_from_events_db.event_store import (
    EventStore,
)


def test_getting_state_from_events_db(event_store: EventStore) -> None:
    """
    Test that the event types are defined correctly.
    """
    shopping_cart_id = str(uuid())
    client_id = str(uuid())
    confirmed_at = datetime.now(UTC)
    canceled_at = datetime.now(UTC)
    current_time = datetime.now(UTC)
    shoes_id = str(uuid())
    pair_of_shoes = PricedProductItem(
        product_id=shoes_id, quantity=1, unit_price=Decimal("100.0")
    )
    two_pairs_of_shoes = PricedProductItem(
        product_id=shoes_id, quantity=2, unit_price=Decimal("100.0")
    )
    t_shirt_id = str(uuid())
    t_shirt = PricedProductItem(
        product_id=t_shirt_id, quantity=1, unit_price=Decimal("5.0")
    )
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
                shopping_cart_id=shopping_cart_id, product_item=two_pairs_of_shoes
            )
        ),
        ProductItemAddedToShoppingCart(
            data=ProductItemAddedToShoppingCart.Data(
                shopping_cart_id=shopping_cart_id, product_item=t_shirt
            )
        ),
        ProductItemRemovedFromShoppingCart(
            data=ProductItemRemovedFromShoppingCart.Data(
                shopping_cart_id=shopping_cart_id, product_item=pair_of_shoes
            )
        ),
        ShoppingCartConfirmed(
            data=ShoppingCartConfirmed.Data(
                shopping_cart_id=shopping_cart_id, confirmed_at=confirmed_at
            )
        ),
        ShoppingCartCanceled(
            data=ShoppingCartCanceled.Data(
                shopping_cart_id=shopping_cart_id, canceled_at=canceled_at
            )
        ),
    ]
    stream_name = f"shopping_cart_{shopping_cart_id}"
    append_to_stream(event_store, stream_name, events)
    events_from_db = read_stream(event_store, stream_name)
    shopping_cart = get_shopping_cart_from_events(events_from_db)

    assert shopping_cart.id == shopping_cart_id
    assert shopping_cart.client_id == client_id
    assert shopping_cart.status == ShoppingCartStatus.Pending
    assert shopping_cart.product_items == [pair_of_shoes, t_shirt]
    assert shopping_cart.opened_at == current_time
    assert shopping_cart.confirmed_at == confirmed_at
    assert shopping_cart.canceled_at == canceled_at
