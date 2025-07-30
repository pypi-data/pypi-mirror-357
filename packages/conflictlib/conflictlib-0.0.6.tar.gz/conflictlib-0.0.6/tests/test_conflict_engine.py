from conflictlib.rules import DeconflictionRule


from tests.utils import generate_seats


def test_conflict_detection_with_adding_reserved_seat():
    seats = generate_seats(30)
    all_unique = DeconflictionRule("unique_for_set(existing, new, 'seat_id')").matches(
        {"existing": seats, "new": {"seat_id": "A1"}}
    )
    assert not all_unique


def test_conflict_detection_with_existing_conflict_seat():
    seats = generate_seats(30, add_conflict=True)
    all_unique = DeconflictionRule("unique(__root__, 'seat_id')").matches(seats)
    assert not all_unique


def test_conflict_detection_with_no_conflicting_seats():
    seats = generate_seats(30)
    all_unique = DeconflictionRule("unique(__root__, 'seat_id')").matches(seats)
    assert all_unique


def test_getting_conflict_detection_duplicates():
    seats = generate_seats(30, add_conflict=True)
    dupes = DeconflictionRule("get_duplicates(__root__, 'seat_id')").evaluate(seats)
    assert len(dupes) == 1


def test_getting_conflict_detection_no_duplicates():
    seats = generate_seats(30)
    dupes = DeconflictionRule("get_duplicates(__root__, 'seat_id')").evaluate(seats)
    assert len(dupes) == 0


def test_conflict_detection_with_adding_unreserved_seat():

    seats = generate_seats(30)
    all_unique = DeconflictionRule("unique_for_set(existing, new, 'seat_id')").matches(
        {"existing": seats, "new": {"seat_id": "Z1"}}
    )

    assert all_unique
