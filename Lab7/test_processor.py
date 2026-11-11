import math
import pytest
from hypothesis import given, strategies as st

from processor import (
    parse_walk_schedule,
    compute_pace_per_pet,
    lookup_temperament_surcharge,
)


# Hypothesis fuzz tests: malformed/edge-case strings must fail safely
@given(st.text() | st.none())
def test_parse_walk_schedule_no_crash(s):
    try:
        result = parse_walk_schedule(s)
        assert isinstance(result, str)
    except (TypeError, ValueError):
        pass


@given(st.text() | st.none())
def test_compute_pace_per_pet_safe(s):
    try:
        result = compute_pace_per_pet(s)
        assert isinstance(result, (int, float))
        assert math.isfinite(result)
    except (TypeError, ValueError):
        pass


@given(st.text() | st.none())
def test_lookup_temperament_surcharge_safe(s):
    try:
        result = lookup_temperament_surcharge(s)
        assert result in (0.0, 5.0, 12.0, 20.0)
    except (TypeError, ValueError):
        pass


# Valid schedule behavior
@pytest.mark.parametrize(
    "schedule, expected",
    [
        ("2-30-YES", "Walk: 2 pets, 30 mins - Total $45.00"),
        ("1-20-NO", "Walk: 1 pets, 20 mins - Total $25.00"),
        ("3-45-YES", "Walk: 3 pets, 45 mins - Total $65.00"),
    ],
)
def test_valid_walk_schedules(schedule, expected):
    assert parse_walk_schedule(schedule) == expected


@pytest.mark.parametrize("bad_schedule", [
    "", "1-30", "1-30-YES-extra", "a-30-YES", "1-x-YES",
    "0-30-YES", "-1-30-YES", "1-0-YES", "1-30-MAYBE",
])
def test_invalid_walk_schedules_rejected(bad_schedule):
    with pytest.raises(ValueError):
        parse_walk_schedule(bad_schedule)


def test_schedule_none_rejected():
    with pytest.raises(TypeError):
        parse_walk_schedule(None)


# Valid pace behavior
@pytest.mark.parametrize(
    "metrics, expected",
    [("45/3", 15.0), ("10/2", 5.0), ("7.5/2", 3.75)],
)
def test_valid_pace(metrics, expected):
    assert compute_pace_per_pet(metrics) == expected


@pytest.mark.parametrize(
    "bad_metrics",
    ["", "45", "45/3/2", "abc/2", "45/abc", "45/0", "0/2", "-5/2",
     "nan/2", "inf/2", "45/nan"],
)
def test_invalid_pace_rejected(bad_metrics):
    with pytest.raises(ValueError):
        compute_pace_per_pet(bad_metrics)


def test_pace_none_rejected():
    with pytest.raises(TypeError):
        compute_pace_per_pet(None)


# Supported temperament names (full names, case-insensitive)
@pytest.mark.parametrize(
    "code, expected",
    [
        ("CALM", 0.0), ("PLAYFUL", 5.0), ("REACTIVE", 12.0),
        ("AGGRESSIVE", 20.0), (" calm ", 0.0), ("playful", 5.0),
    ],
)
def test_supported_temperaments(code, expected):
    assert lookup_temperament_surcharge(code) == expected


@pytest.mark.parametrize(
    "bad_code", ["", "XYZ", "CA", "AGGRESSIVE?", "PLAY", "UNKNOWN"]
)
def test_unknown_temperament_is_rejected(bad_code):
    with pytest.raises(ValueError):
        lookup_temperament_surcharge(bad_code)


def test_temperament_none_rejected():
    with pytest.raises(TypeError):
        lookup_temperament_surcharge(None)
