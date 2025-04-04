from typing import Callable


def merge[T](
    array: list[T],
    item: T,
    where: Callable[[T], bool],
    on_existing: Callable[[T, T], T | None],
    on_not_found: Callable[[T], T | None] = lambda _: None,
) -> list[T]:
    """Merges an item into a list based on a condition, allowing custom logic.

    This function iterates through a given list (`array`) and attempts to find an
    element that satisfies the `where` condition. Based on whether a match is
    found, it applies custom logic defined by the `on_existing` or `on_not_found`
    callbacks to determine the final state of the list.

    The `on_existing` function is called if an element matching the `where`
    condition is found. It receives both the existing element from the list and the
    `item` being merged. It should return the updated element to be kept in the
    list, or `None` to effectively remove the element.

    The `on_not_found` function is called if no element in the list satisfies the
    `where` condition. It receives the `item` being merged and should return a new
    element to be added to the list, or `None` to add nothing.

    Args:
        array: The list to merge the item into.
        item: The item providing the data for the merge operation.
        where: A callable that takes an element from the array and returns
            `True` if it's the target element for merging, `False` otherwise.
        on_existing: A callable invoked when an element matching `where` is found.
            It receives `(existing_element, item)` and returns the element
            to include in the result list, or `None` to remove it.
        on_not_found: A callable invoked if no element matching `where` is found.
            It receives `(item)` and returns a new element to append to the
            list, or `None` to add nothing. Defaults to returning `None`.

    Returns:
        A new list reflecting the result of the merge operation.

    Doctests:
        >>> # Scenario 1: Add quantity to an existing product item
        >>> cart_items = [
        ...     {"product_id": "P1", "quantity": 2, "unit_price": 10.0},
        ...     {"product_id": "P2", "quantity": 1, "unit_price": 25.0}
        ... ]
        >>> item_to_add = {"product_id": "P1", "quantity": 3, "unit_price": 10.0}
        >>> def combine_quantity(existing, new):
        ...     existing["quantity"] += new["quantity"]
        ...     return existing
        >>> merge(
        ...     cart_items,
        ...     item_to_add,
        ...     where=lambda p: p["product_id"] == item_to_add["product_id"] and p["unit_price"] == item_to_add["unit_price"],
        ...     on_existing=combine_quantity
        ... )
        [{'product_id': 'P1', 'quantity': 5, 'unit_price': 10.0}, {'product_id': 'P2', 'quantity': 1, 'unit_price': 25.0}]

        >>> # Scenario 2: Add a completely new product item
        >>> cart_items = [
        ...     {"product_id": "P1", "quantity": 2, "unit_price": 10.0}
        ... ]
        >>> new_product = {"product_id": "P3", "quantity": 1, "unit_price": 50.0}
        >>> def add_new(item): return item # Simply return the item to add it
        >>> merge(
        ...     cart_items,
        ...     new_product,
        ...     where=lambda p: p["product_id"] == new_product["product_id"],
        ...     on_existing=lambda e, n: e, # Should not be called in this case
        ...     on_not_found=add_new
        ... )
        [{'product_id': 'P1', 'quantity': 2, 'unit_price': 10.0}, {'product_id': 'P3', 'quantity': 1, 'unit_price': 50.0}]

        >>> # Scenario 3: Attempt to add an item that already exists (different price)
        >>> # In this case, `where` won't match, so `on_not_found` adds it as a new line item.
        >>> cart_items = [
        ...     {"product_id": "P1", "quantity": 2, "unit_price": 10.0}
        ... ]
        >>> item_different_price = {"product_id": "P1", "quantity": 1, "unit_price": 12.0}
        >>> merge(
        ...     cart_items,
        ...     item_different_price,
        ...     where=lambda p: p["product_id"] == item_different_price["product_id"] and p["unit_price"] == item_different_price["unit_price"],
        ...     on_existing=combine_quantity, # Won't be called
        ...     on_not_found=lambda item: item # Add the new item
        ... )
        [{'product_id': 'P1', 'quantity': 2, 'unit_price': 10.0}, {'product_id': 'P1', 'quantity': 1, 'unit_price': 12.0}]

        >>> # Scenario 4: Remove an item by returning None from on_existing
        >>> cart_items = [
        ...     {"product_id": "P1", "quantity": 5, "unit_price": 10.0},
        ...     {"product_id": "P2", "quantity": 1, "unit_price": 25.0}
        ... ]
        >>> item_to_remove = {"product_id": "P1", "quantity": 5, "unit_price": 10.0} # Data used by 'where'
        >>> def remove_item(existing, new): return None # Return None to remove
        >>> merge(
        ...     cart_items,
        ...     item_to_remove,
        ...     where=lambda p: p["product_id"] == item_to_remove["product_id"],
        ...     on_existing=remove_item
        ... )
        [{'product_id': 'P2', 'quantity': 1, 'unit_price': 25.0}]

        >>> # Scenario 5: Item not found, and on_not_found returns None (no change)
        >>> cart_items = [
        ...     {"product_id": "P1", "quantity": 2, "unit_price": 10.0}
        ... ]
        >>> item_not_present = {"product_id": "P4", "quantity": 1, "unit_price": 100.0}
        >>> merge(
        ...     cart_items,
        ...     item_not_present,
        ...     where=lambda p: p["product_id"] == item_not_present["product_id"],
        ...     on_existing=lambda e, n: e, # Won't be called
        ...     on_not_found=lambda item: None # Default behavior, explicitly shown
        ... )
        [{'product_id': 'P1', 'quantity': 2, 'unit_price': 10.0}]
    """
    was_found = False
    result: list[T] = []

    # Merge the existing item if matches condition
    for p in array:
        if not where(p):
            result.append(p)
        else:
            was_found = True
            updated_item = on_existing(p, item)
            if updated_item is not None:
                result.append(updated_item)

    # If item was not found and on_not_found action is defined
    # try to generate new item
    if not was_found:
        new_item_to_add = on_not_found(item)
        if new_item_to_add is not None:
            result.append(new_item_to_add)
    return result
