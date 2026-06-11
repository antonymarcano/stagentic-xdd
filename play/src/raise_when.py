from collections.abc import Callable


def raise_when(
        erroneous_items: list, *,
        raising_error: type[Exception],
        with_message: Callable[[list], str],
) -> None:
    if erroneous_items:
        raise raising_error(
            with_message(erroneous_items)
        )
