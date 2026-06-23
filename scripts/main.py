# from functools import wraps
from contextlib import contextmanager
from datetime import datetime


def dict_comprehension():
    ticket_types = [
        {"id": 1, "name": "General", "price": 25.00},
        {"id": 2, "name": "VIP", "price": 75.00},
        {"id": 3, "name": "Early Bird", "price": 15.00},
    ]

    ticket_types_lookup = {
        ticket_type["id"]: ticket_type
        for ticket_type in ticket_types
        if ticket_type["price"] < 50
    }
    return ticket_types_lookup


def nested_list_comprehension():
    ticket_types_with_tickets = [
        {"id": 1, "name": "General", "ticket_ids": [101, 102, 103]},
        {"id": 2, "name": "VIP", "ticket_ids": [201, 202]},
        {"id": 3, "name": "Early Bird", "ticket_ids": []},
    ]

    return [
        ticket_id
        for ticket_type in ticket_types_with_tickets
        for ticket_id in ticket_type["ticket_ids"]
    ]


def rest_unpacking():
    prices = [25.00, 75.00, 15.00, 50.00, 30.00]

    cheapest, *middle, most_expensive = prices

    return cheapest, most_expensive, middle


def log_call(func):
    # @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Called with args={args}, kwargs={kwargs}")
        return func(*args, **kwargs)

    return wrapper


@log_call
def add(a, b):
    return a + b


def batch(items, size):
    current = 0
    arr = []

    for item in items:
        arr.append(item)
        current += 1

        if current == size:
            yield arr
            current = 0
            arr = []

    if current != 0:
        yield arr


# for chunk in batch(
#     [1, 2, 3, 4, 5, 6],
#     3,
# ):
#     print(chunk)


@contextmanager
def timer():
    print("now")
    now = datetime.now()
    try:
        yield
    finally:
        result = datetime.now() - now
        print(f"Elapsed: {result.seconds}.{result.microseconds // 100}s")


# with timer():
#     total = sum(range(10_000_000))
# raise ValueError("oops")


def zip_lists():
    ticket_names = ["General", "VIP", "Early Bird"]
    ticket_prices = [25.00, 75.00, 15.00]

    return {name: price for name, price in zip(ticket_names, ticket_prices)}


def sorted_by_starts_at():
    events = [
        {"title": "Jazz Night", "starts_at": "2026-08-01"},
        {"title": "Tech Conf", "starts_at": "2026-06-15"},
        {"title": "Food Fest", "starts_at": "2026-07-10"},
    ]

    return [e["title"] for e in sorted(events, key=lambda event: event["starts_at"])]


def enumarate_waitlist():
    waitlist = ["alice@email.com", "bob@email.com", "carol@email.com"]

    return [f"{index}: {email}" for index, email in enumerate(waitlist, start=1)]


# print(enumarate_waitlist())
