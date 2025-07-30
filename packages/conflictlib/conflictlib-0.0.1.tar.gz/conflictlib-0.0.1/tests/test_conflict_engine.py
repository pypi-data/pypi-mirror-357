import json
import pytest
from pathlib import Path
from conflictlib.engine import ConflictEngine, ConflictReport

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name):
    path = FIXTURE_DIR / name
    with open(path) as f:
        return json.load(f)


@pytest.mark.parametrize("fixture_name", [
    "theater_seat_reservation.json",
    "warehouse_dock_scheduling.json",
    "drone_airspace_scheduling.json"
])
def test_conflict_detection(fixture_name):
    fixture = load_fixture(fixture_name)

    engine = ConflictEngine(rules=[fixture["rule"]])
    result: ConflictReport = engine.check_conflict(
        new=fixture["proposed_allocation"],
        existing=fixture["existing_allocations"]
    )

    assert isinstance(result, ConflictReport), "Engine must return ConflictReport"
    assert result.conflict is True, f"Expected conflict for fixture {fixture_name}"
    assert result.rule == fixture["rule"]["type"]
    assert result.conflicting_ids, f"Should report at least one conflicting resource for {fixture_name}"
    assert result.message, "Conflict report should include a human-readable message"
    assert all(dim in result.dimensions for dim in fixture["rule"]["dimensions"])