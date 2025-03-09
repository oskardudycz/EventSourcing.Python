from typing import Callable


def merge[T](
    array: list[T],
    item: T,
    where: Callable[[T], bool],
    on_existing: Callable[[T], T],
    on_not_found: Callable[[], T | None] = lambda: None,
) -> list[T]:
    was_found = False
    result = []

    # Merge the existing item if matches condition
    for p in array:
        if not where(p):
            result.append(p)
        else:
            was_found = True
            updated_item = on_existing(p)
            if updated_item is not None:
                result.append(updated_item)

    # If item was not found and on_not_found action is defined
    # try to generate new item
    if not was_found:
        new_item = on_not_found()
        if new_item is not None:
            result.append(new_item)
    return result
