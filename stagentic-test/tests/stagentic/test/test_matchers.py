import pytest
from hamcrest import assert_that, equal_to

from stagentic.test.matchers import contains_any, contains_strings


class TestContainsStrings:
    def test_matches_text_containing_every_substring(self):
        assert_that("alpha and beta", contains_strings("alpha", "beta"))

    def test_does_not_match_when_a_substring_is_missing(self):
        with pytest.raises(AssertionError) as excinfo:
            assert_that("only alpha", contains_strings("alpha", "beta"))

        assert_that(str(excinfo.value), equal_to(
            "\nExpected: (a string containing 'alpha' and a string containing 'beta')\n"
            "     but: a string containing 'beta' was 'only alpha'\n"
        ))

    def test_does_not_match_when_the_first_substring_is_missing(self):
        with pytest.raises(AssertionError) as excinfo:
            assert_that("only beta", contains_strings("alpha", "beta"))

        assert_that(str(excinfo.value), equal_to(
            "\nExpected: (a string containing 'alpha' and a string containing 'beta')\n"
            "     but: a string containing 'alpha' was 'only beta'\n"
        ))


class TestContainsAny:
    def test_matches_text_containing_any_substring(self):
        assert_that("alpha and beta", contains_any("alpha", "beta"))

    def test_matches_text_containing_only_one_substring(self):
        assert_that("only beta", contains_any("alpha", "beta"))

    def test_does_not_match_when_no_substring_is_present(self):
        with pytest.raises(AssertionError) as excinfo:
            assert_that("only gamma", contains_any("alpha", "beta"))

        assert_that(str(excinfo.value), equal_to(
            "\nExpected: (a string containing 'alpha' or a string containing 'beta')\n"
            "     but: was 'only gamma'\n"
        ))
