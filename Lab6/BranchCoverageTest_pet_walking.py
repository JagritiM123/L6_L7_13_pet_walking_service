import pytest
from pet_walking_service import process_walking_routes, inspect_gps_collars


class TestProcessWalkingRoutesBranches:
    def test_invalid_routes_type(self):
        with pytest.raises(ValueError):
            process_walking_routes("not-a-list", 10)

    def test_negative_transport_fee(self):
        with pytest.raises(ValueError):
            process_walking_routes([], -1)

    def test_unconfirmed_route_skipped(self):
        result = process_walking_routes([{"route_confirmed": False}], 10)
        assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}

    @pytest.mark.parametrize("session_type,fee", [
        ("standard_60", 35.0), ("standard_30", 22.0), ("express_15", 14.0)
    ])
    def test_each_supported_session_type(self, session_type, fee):
        route = {"route_confirmed": True, "session_type": session_type,
                 "walks": [{"num_pets": 1}]}
        result = process_walking_routes([route], 0)
        assert result["total_revenue"] == fee + 5.0
        assert result["status"] == "COMPLETED"

    def test_unknown_session_type_increments_incident(self):
        routes = [{"route_confirmed": True, "session_type": "unknown", "walks": []}]
        result = process_walking_routes(routes, 0)
        assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}

    def test_invalid_pet_count_skipped(self):
        route = {"route_confirmed": True, "session_type": "standard_30",
                 "walks": [{"num_pets": 0}, {"num_pets": -1}, {"num_pets": 1}]}
        result = process_walking_routes([route], 0)
        assert result["total_revenue"] == 27.0

    def test_aggression_alert_standard_60_aborts_route(self):
        route = {"route_confirmed": True, "session_type": "standard_60",
                 "walks": [{"num_pets": 1}, {"num_pets": 1, "aggression_alert": True},
                          {"num_pets": 2}]}
        result = process_walking_routes([route], 0)
        assert result["total_revenue"] == 0.0

    def test_aggression_alert_other_session_keeps_processing(self):
        route = {"route_confirmed": True, "session_type": "standard_30",
                 "walks": [{"num_pets": 1, "aggression_alert": True},
                          {"num_pets": 2}]}
        result = process_walking_routes([route], 0)
        assert result["total_revenue"] == 32.0

    def test_more_than_three_pets_discount_branch(self):
        route = {"route_confirmed": True, "session_type": "standard_30",
                 "walks": [{"num_pets": 4}]}
        result = process_walking_routes([route], 0)
        assert result["total_revenue"] == (22.0 + 4 * 8.0) * 0.90

    def test_three_or_fewer_pets_regular_branch(self):
        route = {"route_confirmed": True, "session_type": "standard_30",
                 "walks": [{"num_pets": 3}]}
        result = process_walking_routes([route], 0)
        assert result["total_revenue"] == 37.0

    def test_medication_true_and_false_branches(self):
        route = {"route_confirmed": True, "session_type": "standard_30",
                 "walks": [{"num_pets": 1, "needs_meds": True},
                          {"num_pets": 1, "needs_meds": False}]}
        # (22 + 5 + 6) + (22 + 5) = 60
        result = process_walking_routes([route], 0)
        assert result["total_revenue"] == 60.0

    def test_weekend_true_and_false_routes(self):
        routes = [
            {"route_confirmed": True, "session_type": "standard_30",
             "walks": [{"num_pets": 2}], "is_weekend": True},
            {"route_confirmed": True, "session_type": "standard_30",
             "walks": [{"num_pets": 1}], "is_weekend": False},
        ]
        # Weekend: 22 + (2*5) + 5 transport = 37; weekday: 27; total 64
        result = process_walking_routes(routes, 5)
        assert result["total_revenue"] == 64.0

    def test_incident_audit_threshold(self):
        routes = [{"route_confirmed": True, "session_type": "unknown"} for _ in range(5)]
        result = process_walking_routes(routes, 0)
        assert result["status"] == "INCIDENT_AUDIT"

    def test_completed_status(self):
        route = {"route_confirmed": True, "session_type": "standard_30",
                 "walks": [{"num_pets": 1}]}
        assert process_walking_routes([route], 0)["status"] == "COMPLETED"


class TestInspectGpsCollarsBranches:
    def test_empty_matrix(self):
        assert inspect_gps_collars([]) == "NO_DATA"

    def test_single_low_signal_is_online(self):
        assert inspect_gps_collars([[10]]) == "ONLINE"

    def test_two_consecutive_low_signals_alert(self):
        assert inspect_gps_collars([[10, 15]]) == "LOST_SIGNAL_ALERT"

    def test_low_signal_streak_reset_by_good_signal(self):
        assert inspect_gps_collars([[10, 25, 15]]) == "ONLINE"

    def test_alert_in_second_collar(self):
        assert inspect_gps_collars([[10, 25], [19, 18]]) == "LOST_SIGNAL_ALERT"
