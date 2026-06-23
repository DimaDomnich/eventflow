import datetime
import csv
import psycopg2
from main import batch


conn = psycopg2.connect("postgresql://eventflow:eventflow@localhost:5432/eventflow")
cursor = conn.cursor()

before = datetime.datetime.now()

with open("bulk_test_data_100_000.csv", "r", newline="") as f:
    reader = csv.reader(f)

    next(reader, None)

    reader_list = list(reader)

    for rows in batch(reader_list, 500):
        cursor.executemany(
            "INSERT INTO bulk_test_tickets (ticket_id, event_id, attendee_email, price, status) VALUES (%s, %s, %s, %s, %s)",
            tuple(rows),
        )

conn.commit()

print(f"{datetime.datetime.now() - before} passed")
