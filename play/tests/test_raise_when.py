from contextlib import nullcontext as does_not_raise

import pytest
from stagentic.test.cases import case

from raise_when import raise_when


class TestRaiseWhen:
    def test_does_not_raise_when_there_are_no_items(self):
        no_erroneous_items_to_raise_about = []
        with does_not_raise():
            raise_when(
                no_erroneous_items_to_raise_about,
                raising_error=ValueError,
                with_message=lambda items: "dummy message"
            )

    @pytest.mark.parametrize("raising_error, erroneous_items, with_message, expected_message", [
        case(
            "items-in-message",
            raising_error=ValueError,
            erroneous_items=["a", "b"],
            with_message=lambda items: f"got {items}",
            expected_message="got ['a', 'b']",
        ),
        case(
            "assertion-error",
            raising_error=AssertionError,
            erroneous_items=["x"],
            with_message=lambda items: "boom",
            expected_message="boom",
        ),
    ])
    def test_raises_the_given_error_with_the_formatted_message(
            self, raising_error, erroneous_items, with_message, expected_message,
    ):
        with pytest.raises(raising_error) as excinfo:
            raise_when(
                erroneous_items,
                raising_error=raising_error,
                with_message=with_message
            )

        assert str(excinfo.value) == expected_message
