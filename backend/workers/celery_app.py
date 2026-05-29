"""
Celery application and task definitions.

Broker and result backend both point to Upstash Redis via the standard Redis
URL from the environment.  Three periodic tasks are registered:
  - scrape_all_countries   — runs the full scrape + detect + alert + embed pipeline
  - check_change_events    — placeholder (change detection is handled inline above)
  - send_pending_alerts    — re-sends any unsent alert rows

Beat schedule can be adjusted without code changes by updating the crontab
entries below.
"""

import asyncio
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
    """Run the full scrape → detect changes → send alerts → re-embed pipeline."""
    from services.ingest_and_alert import run_ingest_and_alert
    result = asyncio.run(run_ingest_and_alert())
    print(
        f"[celery] scrape_all_countries complete: "
        f"{result['docs_scraped']} docs, "
        f"{result['changes_detected']} changes, "
        f"{result['alerts_sent']} alerts sent, "
        f"{result['chunks_stored']} chunks stored"
    )
    return result


@app.task(name="tasks.check_change_events")
def check_change_events():
    """No-op: change detection runs inline in scrape_all_countries."""
    pass


@app.task(name="tasks.send_pending_alerts")
def send_pending_alerts():
    """Re-fan-out any policy_changes rows that have not yet triggered alerts."""
    from db.client import admin_client
    from services.alert_engine import process_changes

    # Find recent changes that may not have been alertted yet
    result = admin_client().table("policy_changes").select("*").order("detected_at", desc=True).limit(20).execute()
    changes = []
    for row in result.data or []:
        country_result = admin_client().table("countries").select("code").eq("id", row.get("country_id", "")).execute()
        if country_result.data:
            changes.append({
                "country_code": country_result.data[0]["code"],
                "visa_type": row.get("visa_type", ""),
                "source_url": "",
                "change_summary": row.get("change_summary", ""),
            })

    if changes:
        total = asyncio.run(process_changes(changes))
        print(f"[celery] send_pending_alerts: {total} alert(s) sent")
    else:
        print("[celery] send_pending_alerts: no pending changes")


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
