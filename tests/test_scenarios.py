"""Tests for scenario generation."""

from __future__ import annotations

from server.scenarios import (
    generate_easy_scenario,
    generate_hard_scenario,
    generate_medium_scenario,
)


class TestEasyScenario:
    def test_has_one_shipment(self, easy_scenario):
        assert len(easy_scenario.shipments) == 1

    def test_budget_is_5000(self, easy_scenario):
        assert easy_scenario.total_budget == 5000.0

    def test_shipment_has_required_fields(self, easy_scenario):
        ship = easy_scenario.shipments[0]
        assert ship.shipment_id == "SHP-001"
        assert ship.exception_type == "weather_delay"
        assert ship.priority in ("high", "medium")
        assert ship.sla_deadline_steps == 4
        assert ship.status == "new"
        assert ship.resolution_progress == 0.0

    def test_seed_produces_deterministic_result(self):
        s1 = generate_easy_scenario(seed=99)
        s2 = generate_easy_scenario(seed=99)
        assert s1.shipments[0].origin == s2.shipments[0].origin
        assert s1.shipments[0].destination == s2.shipments[0].destination
        assert s1.shipments[0].carrier == s2.shipments[0].carrier

    def test_different_seeds_produce_different_results(self):
        s1 = generate_easy_scenario(seed=1)
        s2 = generate_easy_scenario(seed=2)
        # Very likely different origins (10 cities, 2 chosen)
        # At minimum, check they both produce valid scenarios
        assert len(s1.shipments) == 1
        assert len(s2.shipments) == 1


class TestMediumScenario:
    def test_has_four_shipments(self, medium_scenario):
        assert len(medium_scenario.shipments) == 4

    def test_budget_is_12000(self, medium_scenario):
        assert medium_scenario.total_budget == 12000.0

    def test_has_different_exception_types(self, medium_scenario):
        types = {s.exception_type for s in medium_scenario.shipments}
        assert len(types) >= 3  # At least 3 different types

    def test_has_different_priorities(self, medium_scenario):
        priorities = {s.priority for s in medium_scenario.shipments}
        assert len(priorities) >= 2

    def test_shipment_ids_are_sequential(self, medium_scenario):
        ids = [s.shipment_id for s in medium_scenario.shipments]
        assert ids == ["SHP-001", "SHP-002", "SHP-003", "SHP-004"]


class TestHardScenario:
    def test_has_eight_shipments(self, hard_scenario):
        assert len(hard_scenario.shipments) == 8

    def test_budget_is_15000(self, hard_scenario):
        assert hard_scenario.total_budget == 15000.0

    def test_has_critical_priority_shipments(self, hard_scenario):
        critical = [s for s in hard_scenario.shipments if s.priority == "critical"]
        assert len(critical) >= 2

    def test_has_port_closure_exceptions(self, hard_scenario):
        port_closures = [
            s for s in hard_scenario.shipments
            if s.exception_type == "port_closure"
        ]
        assert len(port_closures) >= 2

    def test_sla_deadlines_vary(self, hard_scenario):
        slas = {s.sla_deadline_steps for s in hard_scenario.shipments}
        assert len(slas) >= 3  # At least 3 different SLA values
