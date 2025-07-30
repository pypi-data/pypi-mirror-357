from conflictlib.rules import DeconflictionRule


from utils import generate_seats
import time


def run_benchmark():
    BENCHMARK_CASES = [10, 100, 1000, 10000]
    for num_seats in BENCHMARK_CASES:
        seats = generate_seats(num_seats, add_conflict=True)
        start = time.time()
        DeconflictionRule("unique(__root__, 'seat_id')").matches(seats)
        end = time.time()
        print(
            f"**** TIME TO CHECK CONFLICTS FOR {num_seats}: {(end-start) *1000} Milliseconds ****"
        )


if __name__ == "__main__":
    run_benchmark()
