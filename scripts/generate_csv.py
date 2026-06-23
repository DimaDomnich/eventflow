import argparse
import csv
import random


def generate_csv(path: str, num_rows: int) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ticket_id", "event_id", "attendee_email", "price", "status"])

        statuses = ["confirmed", "reserved", "cancelled", "used"]

        for i in range(num_rows):
            writer.writerow(
                [
                    i,
                    random.randint(1, 1000),
                    f"user{i}@example.com",
                    round(random.uniform(10, 200), 2),
                    random.choice(statuses),
                ]
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path", default="bulk_test_data_5_000_000.csv", help="Output CSV file path"
    )
    parser.add_argument(
        "--num-rows", type=int, default=5_000_000, help="Number of rows to generate"
    )
    args = parser.parse_args()

    generate_csv(args.path, args.num_rows)
