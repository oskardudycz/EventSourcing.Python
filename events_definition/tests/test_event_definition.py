from decimal import Decimal
from uuid import uuid4 as uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from events_definition.src.events_definition import (
    PricedProductItem,
    ShoppingCartEvent,
    ShoppingCartOpened,
    ProductItemAddedToShoppingCart,
    ProductItemRemovedFromShoppingCart,
    ShoppingCartConfirmed,
    ShoppingCartCanceled,
)


def test_event_types_should_be_defined(db_session: Session) -> None:
    """
    Test that the event types are defined correctly.
    """
    shopping_cart_id = str(uuid())
    client_id = str(uuid())
    pair_of_socks = PricedProductItem(
        product_id=str(uuid()), quantity=2, unit_price=Decimal("10.0")
    )
    current_time = datetime.now(timezone.utc)

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

    expected_types = [
        "ShoppingCartOpened",
        "ProductItemAddedToShoppingCart",
        "ProductItemRemovedFromShoppingCart",
        "ShoppingCartConfirmed",
        "ShoppingCartCanceled",
    ]

    for event, expected_type in zip(events, expected_types):
        assert event.type == expected_type
