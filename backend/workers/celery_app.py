"""
Celery application and task definitions.

Broker and result backend both point to Upstash Redis via the standard Redis
URL from the environment.  Three periodic tasks are registered:
  - scrape_all_countries   — runs the full scrape + embed + diff pipeline
  - check_change_events    — polls the Redis pub/sub channel for new alerts
  - send_pending_alerts    — fans out any unsent alert rows from Supabase

Beat schedule can be adjusted without code changes by updating the crontab
entries below.
"""

import os
from celery import Celery
from celery.schedules import crontab

app = Celery(
    "exitplan",
    broker=os.getenv("UPSTASH_REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("UPSTASH_REDIS_URL", "redis://localhost:6379/0"),
)

app.conf.timezone = "UTC"


@app.task(name="tasks.scrape_all_countries")
def scrape_all_countries():
    """Celery task: trigger the full scrape + embed + diff pipeline."""
    pass


@app.task(name="tasks.check_change_events")
def check_change_events():
    """Celery task: drain the Redis pub/sub channel and persist change events."""
    pass


@app.task(name="tasks.send_pending_alerts")
def send_pending_alerts():
    """Celery task: query unsent alert rows in Supabase and send emails via Resend."""
    pass


app.conf.beat_schedule = {
    "scrape-daily": {
        "task": "tasks.scrape_all_countries",
        "schedule": crontab(hour=3, minute=0),
    },
    "check-changes-hourly": {
        "task": "tasks.check_change_events",
        "schedule": crontab(minute=0),
    },
    "send-alerts-every-15min": {
        "task": "tasks.send_pending_alerts",
        "schedule": crontab(minute="*/15"),
    },
}
