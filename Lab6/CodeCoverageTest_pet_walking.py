import pytest
from pet_walking_service import process_walking_routes, inspect_gps_collars


@pytest.mark.parametrize("session_type,base_fee", [
    ("standard_60", 35.0), ("standard_30", 22.0), ("express_15", 14.0)
])
def test_revenue_for_session_types(session_type, base_fee):
    route = {"route_confirmed": True, "session_type": session_type,
             "walks": [{"num_pets": 1}]}
    assert process_walking_routes([route], 0)["total_revenue"] == base_fee + 5.0


def test_unconfirmed_route_returns_zero():
    assert process_walking_routes([{"route_confirmed": False}], 0)["status"] == "ZERO_EARNINGS"


def test_route_with_multiple_walks_and_meds():
    route = {"route_confirmed": True, "session_type": "standard_30",
             "walks": [{"num_pets": 1, "needs_meds": True},
                       {"num_pets": 2, "needs_meds": False}]}
    assert process_walking_routes([route], 0)["total_revenue"] == 38.0


def test_aggression_alert_standard_60_zeroes_route():
    route = {"route_confirmed": True, "session_type": "standard_60",
             "walks": [{"num_pets": 1}, {"num_pets": 1, "aggression_alert": True}]}
    assert process_walking_routes([route], 0)["total_revenue"] == 0.0


def test_aggression_alert_standard_30_continues():
    route = {"route_confirmed": True, "session_type": "standard_30",
             "walks": [{"num_pets": 1, "aggression_alert": True}, {"num_pets": 1}]}
    assert process_walking_routes([route], 0)["total_revenue"] == 27.0


def test_pet_count_discount_and_regular_pricing():
    routes = [
        {"route_confirmed": True, "session_type": "standard_30", "walks": [{"num_pets": 4}]},
        {"route_confirmed": True, "session_type": "standard_30", "walks": [{"num_pets": 3}]}
    ]
    expected = (22 + 4*8)*0.9 + (22 + 3*5)
    assert process_walking_routes(routes, 0)["total_revenue"] == expected


def test_weekend_transport_fee():
    route = {"route_confirmed": True, "session_type": "standard_30",
             "walks": [{"num_pets": 1}], "is_weekend": True}
    assert process_walking_routes([route], 5)["total_revenue"] == 32.0


def test_invalid_walks_are_skipped_and_incidents_audited():
    route = {"route_confirmed": True, "session_type": "standard_30",
             "walks": [{"num_pets": 0}, {"num_pets": -1}]}
    assert process_walking_routes([route], 0)["status"] == "ZERO_EARNINGS"


def test_more_than_four_incidents_audit():
    routes = [{"route_confirmed": True, "session_type": "bad"} for _ in range(5)]
    assert process_walking_routes(routes, 0)["status"] == "INCIDENT_AUDIT"


def test_gps_no_data_online_and_alert():
    assert inspect_gps_collars([]) == "NO_DATA"
    assert inspect_gps_collars([[25, 30, 18]]) == "ONLINE"
    assert inspect_gps_collars([[10, 15]]) == "LOST_SIGNAL_ALERT"


def test_gps_signal_streak_reset():
    assert inspect_gps_collars([[10, 25, 10]]) == "ONLINE"
