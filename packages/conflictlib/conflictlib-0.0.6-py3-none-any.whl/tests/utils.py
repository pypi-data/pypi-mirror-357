import math
import string
import uuid


def generate_seats(total_seats: int, add_conflict=False) -> list[str]:
    """
    Generates a list of seat labels based on a total number of seats.

    The function creates a "seating chart" by arranging seats into rows (A, B, C...)
    and columns (1, 2, 3...). It determines the number of columns (the "width")
    in a way that makes the layout as "square" as possible.

    However, it includes a key constraint: it will never use a letter beyond 'Z'.
    If the ideal square layout would require more than 26 rows, the function
    will automatically increase the number of seats per row to ensure all seats
    fit within the 26 available letters.

    Args:
        total_seats: The total number of seats to generate. Must be a
                     positive integer.

    Returns:
        A list of seat objects, where each string is a seat label like "A1".
        The list will contain exactly `total_seats` labels. If the input is
        zero or negative, it returns an empty list.
    """
    if not isinstance(total_seats, int) or total_seats <= 0:
        return []

    # --- Determine the optimal number of columns (width) ---

    # Start by trying to make the layout as "square" as possible
    # A square layout's width is the square root of the total area.
    width = math.ceil(math.sqrt(total_seats))

    # Check if this width would require more than 26 rows (letters)
    if width > 0:
        rows_needed = math.ceil(total_seats / width)
        if rows_needed > 26:
            # If so, we are constrained by the alphabet.
            # Recalculate width to be the minimum size needed to fit all seats
            # within 26 rows.
            width = math.ceil(total_seats / 26)

    # --- Generate the seat labels ---

    seats = []
    letters = string.ascii_uppercase
    dupe_seat = {}

    # Generate seats one by one using the calculated width
    for i in range(total_seats):
        # Determine the row (letter) and column (number) for the current seat
        row_index = i // width
        col_index = i % width

        # Create the seat label (e.g., "A1")
        seat_label = f"{letters[row_index]}{col_index + 1}"
        seats.append({"seat_id": seat_label, "id": str(uuid.uuid4())})
        if add_conflict:
            dupe_seat = {"seat_id": seat_label, "id": str(uuid.uuid4())}
    if add_conflict:
        seats.append(dupe_seat)

    return seats
