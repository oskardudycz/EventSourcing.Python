from decimal import Decimal
from uuid import uuid4 as uuid
from datetime import datetime, UTC
import pytest


from business_logic.src.business_logic import (
    AddProductItemToShoppingCart,
    CancelShoppingCart,
    ConfirmShoppingCart,
    OpenShoppingCart,
    RemoveProductItemFromShoppingCart,
    ShoppingCartException,
    decide,
)
from business_logic.src.business_logic.event_store import (
    EventStore,
)

from business_logic.src.business_logic.shopping_cart import (
    PricedProductItem,
    ShoppingCartEvent,
    ShoppingCartOpened,
    ProductItemAddedToShoppingCart,
    ProductItemRemovedFromShoppingCart,
    ShoppingCartConfirmed,
    get_shopping_cart_from_events,
    empty_shopping_cart,
)


def test_business_logic() -> None:
    """
    Test that the event types are defined correctly.
    """
    event_store: EventStore[ShoppingCartEvent] = EventStore[ShoppingCartEvent]()

    shopping_cart_id = str(uuid())
    client_id = str(uuid())
    confirmed_at = datetime.now(UTC)
    canceled_at = datetime.now(UTC)
    current_time = datetime.now(UTC)
    shoes_id = str(uuid())
    stream_name = f"shopping_cart_{shopping_cart_id}"

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

    result: list[ShoppingCartEvent] = []

    open: OpenShoppingCart = OpenShoppingCart(
        data=OpenShoppingCart.Data(
            shopping_cart_id=shopping_cart_id,
            client_id=client_id,
            now=current_time,
        )
    )
    result = [decide(open, empty_shopping_cart)]
    event_store.append_events(stream_name, result)

    add_two_pairs_of_shoes: AddProductItemToShoppingCart = AddProductItemToShoppingCart(
        data=AddProductItemToShoppingCart.Data(
            shopping_cart_id=shopping_cart_id,
            product_item=two_pairs_of_shoes,
        )
    )
    state = get_shopping_cart_from_events(event_store.read_stream(stream_name))
    result = [decide(add_two_pairs_of_shoes, state)]
    event_store.append_events(stream_name, result)

    add_t_shirt: AddProductItemToShoppingCart = AddProductItemToShoppingCart(
        data=AddProductItemToShoppingCart.Data(
            shopping_cart_id=shopping_cart_id,
            product_item=t_shirt,
        )
    )
    state = get_shopping_cart_from_events(event_store.read_stream(stream_name))
    result = [decide(add_t_shirt, state)]
    event_store.append_events(stream_name, result)

    remove_pair_of_shoes: RemoveProductItemFromShoppingCart = (
        RemoveProductItemFromShoppingCart(
            data=RemoveProductItemFromShoppingCart.Data(
                shopping_cart_id=shopping_cart_id,
                product_item=pair_of_shoes,
            )
        )
    )
    state = get_shopping_cart_from_events(event_store.read_stream(stream_name))
    result = [decide(remove_pair_of_shoes, state)]
    event_store.append_events(stream_name, result)

    confirm: ConfirmShoppingCart = ConfirmShoppingCart(
        data=ConfirmShoppingCart.Data(
            shopping_cart_id=shopping_cart_id,
            now=confirmed_at,
        )
    )
    state = get_shopping_cart_from_events(event_store.read_stream(stream_name))
    result = [decide(confirm, state)]
    event_store.append_events(stream_name, result)

    cancel: CancelShoppingCart = CancelShoppingCart(
        data=CancelShoppingCart.Data(
            shopping_cart_id=shopping_cart_id,
            now=canceled_at,
        )
    )

    # Test that canceling a confirmed shopping cart raises ShoppingCartException
    with pytest.raises(ShoppingCartException):
        state = get_shopping_cart_from_events(event_store.read_stream(stream_name))
        result = [decide(cancel, state)]
        event_store.append_events(stream_name, result)

    expected_events: list[ShoppingCartEvent] = [
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
        # ShoppingCartCanceled(
        #     data=ShoppingCartCanceled.Data(
        #         shopping_cart_id=shopping_cart_id, canceled_at=canceled_at
        #     )
        # ),
    ]

    events_from_db = event_store.read_stream(stream_name)

    assert events_from_db == expected_events
