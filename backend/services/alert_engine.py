"""
Alert fan-out engine.

Consumes change events from the Upstash Redis pub/sub channel (published by
change_detector.py), looks up all users subscribed to the affected country,
and dispatches per-user email alerts via Resend.  Runs as a Celery worker.
"""


async def process_change_event(event: dict):
    """Handle a single change event: look up subscribers and send alerts."""
    pass


async def fetch_subscribers(country_code: str) -> list[dict]:
    """Return all users subscribed to alerts for the given country."""
    pass


async def send_email_alert(user: dict, country_code: str, change_summary: str):
    """Send a Resend email to a single user about a policy change."""
    pass


async def build_alert_email(user: dict, country_code: str, change_summary: str) -> dict:
    """Render the subject and HTML body for an alert email."""
    pass
