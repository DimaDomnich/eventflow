from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

celery = Celery(
    "eventflow",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
    include=["app.tasks.waitlist"],
)
