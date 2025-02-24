import unittest
from decimal import Decimal
from uuid import uuid4 as uuid
from datetime import datetime, timezone


from getting_state_from_events.src.getting_state_from_events import (
    ProductItemRemovedFromShoppingCart,
    ShoppingCartCanceled,
    ShoppingCartConfirmed,
    get_shopping_cart_from_events,
    ShoppingCartStatus,
    PricedProductItem,
    ShoppingCartEvent,
    ShoppingCartOpened,
    ProductItemAddedToShoppingCart,
)


class TestGettingStateFromEvents(unittest.TestCase):
    def test_should_return_the_state_from_the_sequence_of_events(self) -> None:
        """
        Test that the event types are defined correctly.
        """
        shopping_cart_id = str(uuid())
        client_id = str(uuid())
        confirmed_at = datetime.now(timezone.utc)
        canceled_at = datetime.now(timezone.utc)
        current_time = datetime.now(timezone.utc)
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

        shopping_cart = get_shopping_cart_from_events(events)
        assert shopping_cart.id == shopping_cart_id
        assert shopping_cart.client_id == client_id
        assert shopping_cart.status == ShoppingCartStatus.Pending
        assert shopping_cart.product_items == [pair_of_shoes, t_shirt]
        assert shopping_cart.opened_at == current_time
        assert shopping_cart.confirmed_at == confirmed_at
        assert shopping_cart.canceled_at == canceled_at
