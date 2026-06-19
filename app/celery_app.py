from celery import Celery
import os
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv()

celery = Celery(
    "eventflow",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
    include=["app.tasks.waitlist", "app.tasks.order", "app.tasks.event"],
)


celery.conf.beat_schedule = {
    "process-expired-waitlist": {
        "task": "app.tasks.waitlist.process_expired_waitlist",
        "schedule": 60.0,
    },
    "process-finished-events": {
        "task": "app.tasks.event.process_finished_events",
        "schedule": 300.0,
    },
}
