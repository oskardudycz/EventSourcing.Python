from datetime import datetime
from enum import StrEnum
from typing import ClassVar, Literal, cast
from pydantic import BaseModel
from business_logic.src.business_logic.model import Command
from .shopping_cart import (
    PricedProductItem,
    ShoppingCart,
    ShoppingCartEvent,
    ShoppingCartStatus,
    ShoppingCartOpened,
    ProductItemAddedToShoppingCart,
    ProductItemRemovedFromShoppingCart,
    ShoppingCartConfirmed,
    ShoppingCartCanceled,
    Pending,
)


class OpenShoppingCart(Command):
    type: ClassVar[Literal["OpenShoppingCart"]] = "OpenShoppingCart"

    class Data(BaseModel):
        shopping_cart_id: str
        client_id: str
        now: datetime

    data: Data


class AddProductItemToShoppingCart(Command):
    type: ClassVar[Literal["AddProductItemToShoppingCart"]] = (
        "AddProductItemToShoppingCart"
    )

    class Data(BaseModel):
        shopping_cart_id: str
        product_item: PricedProductItem

    data: Data


class RemoveProductItemFromShoppingCart(Command):
    type: ClassVar[Literal["RemoveProductItemFromShoppingCart"]] = (
        "RemoveProductItemFromShoppingCart"
    )

    class Data(BaseModel):
        shopping_cart_id: str
        product_item: PricedProductItem

    data: Data


class ConfirmShoppingCart(Command):
    type: ClassVar[Literal["ConfirmShoppingCart"]] = "ConfirmShoppingCart"

    class Data(BaseModel):
        shopping_cart_id: str
        now: datetime

    data: Data


class CancelShoppingCart(Command):
    type: ClassVar[Literal["CancelShoppingCart"]] = "CancelShoppingCart"

    class Data(BaseModel):
        shopping_cart_id: str
        now: datetime

    data: Data


type ShoppingCartCommand = (
    OpenShoppingCart
    | AddProductItemToShoppingCart
    | RemoveProductItemFromShoppingCart
    | ConfirmShoppingCart
    | CancelShoppingCart
)


class ShoppingCartErrors(StrEnum):
    CartAlreadyExists = "CartAlreadyExists"
    CartIsAlreadyClosed = "CartIsAlreadyClosed"
    ProductItemNotFound = "ProductItemNotFound"
    CartIsEmpty = "CartIsEmpty"
    UnknownEvent = "UnknownEvent"
    UnknownCommand = "UnknownCommand"


class ShoppingCartException(Exception):
    pass


def assert_product_item_exists(
    product_items: list[PricedProductItem], product_item: PricedProductItem
) -> None:
    """Check if a product item exists in a list of items."""
    if product_item not in product_items:
        raise ShoppingCartException(ShoppingCartErrors.ProductItemNotFound)


def decide(command: ShoppingCartCommand, state: ShoppingCart) -> ShoppingCartEvent:
    match command:
        case OpenShoppingCart(data=command_data):
            if state.status != ShoppingCartStatus.Empty:
                raise ShoppingCartException(ShoppingCartErrors.CartAlreadyExists)
            return ShoppingCartOpened(
                data=ShoppingCartOpened.Data(
                    shopping_cart_id=command_data.shopping_cart_id,
                    client_id=command_data.client_id,
                    opened_at=command_data.now,
                )
            )
        case AddProductItemToShoppingCart(data=command_data):
            if state.status != ShoppingCartStatus.Pending:
                raise ShoppingCartException(ShoppingCartErrors.CartAlreadyExists)
            return ProductItemAddedToShoppingCart(
                data=ProductItemAddedToShoppingCart.Data(
                    shopping_cart_id=command_data.shopping_cart_id,
                    product_item=command_data.product_item,
                )
            )
        case RemoveProductItemFromShoppingCart(data=command_data):
            if state.status != ShoppingCartStatus.Pending:
                raise ShoppingCartException(ShoppingCartErrors.CartIsAlreadyClosed)
            # We already checked that state is Pending, so we can safely access product_items
            pending_state = cast(Pending, state)
            assert_product_item_exists(
                pending_state.product_items, command_data.product_item
            )
            return ProductItemRemovedFromShoppingCart(
                data=ProductItemRemovedFromShoppingCart.Data(
                    shopping_cart_id=command_data.shopping_cart_id,
                    product_item=command_data.product_item,
                )
            )
        case ConfirmShoppingCart(data=command_data):
            # First check if the cart is in Pending status
            if state.status != ShoppingCartStatus.Pending:
                raise ShoppingCartException(ShoppingCartErrors.CartAlreadyExists)

            # At this point we know it's a Pending cart, so we can safely check product_items
            pending_state = cast(Pending, state)
            if not pending_state.product_items:
                raise ShoppingCartException(ShoppingCartErrors.CartIsEmpty)
            return ShoppingCartConfirmed(
                data=ShoppingCartConfirmed.Data(
                    shopping_cart_id=command_data.shopping_cart_id,
                    confirmed_at=command_data.now,
                )
            )
        case CancelShoppingCart(data=command_data):
            if state.status != ShoppingCartStatus.Pending:
                raise ShoppingCartException(ShoppingCartErrors.CartIsAlreadyClosed)
            return ShoppingCartCanceled(
                data=ShoppingCartCanceled.Data(
                    shopping_cart_id=command_data.shopping_cart_id,
                    canceled_at=command_data.now,
                )
            )
        case _:
            raise ShoppingCartException(ShoppingCartErrors.UnknownCommand)
