from conversion import miles_to_km


def test_one_mile_is_about_1_60934_km():
    assert miles_to_km(1) == 1.60934
