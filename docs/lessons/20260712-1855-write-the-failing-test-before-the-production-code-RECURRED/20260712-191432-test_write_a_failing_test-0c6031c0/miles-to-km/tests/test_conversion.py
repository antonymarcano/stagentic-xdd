from conversion import miles_to_km


def test_one_mile_is_1_609344_km():
    assert miles_to_km(1) == 1.609344
