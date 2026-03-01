"""examples/scheduled.py – SnapAPI v2 Python SDK
Demonstrates: Scheduled screenshots, Webhooks, API Keys
"""
import os
from snapapi import SnapAPI, CreateScheduledOptions, CreateWebhookOptions

client = SnapAPI(api_key=os.environ.get("SNAPAPI_KEY", "sk_live_YOUR_KEY"))


def scheduled_demo():
    print("=== Scheduled Screenshots ===")

    # Create a job – every day at 09:00 UTC
    job = client.scheduled_create(CreateScheduledOptions(
        url="https://example.com",
        cron_expression="0 9 * * *",
        format="png",
        width=1280,
        height=800,
        full_page=True,
        webhook_url="https://webhook.site/your-id",
    ))
    print(f"Created job: {job.id}  next run: {job.next_run}")

    # List all jobs
    jobs = client.scheduled_list()
    for j in jobs:
        print(f"  {j.id}  {j.cron_expression}  next={j.next_run}")

    # Delete
    del_result = client.scheduled_delete(job.id)
    print("Deleted:", del_result.success)


def webhooks_demo():
    print("\n=== Webhooks ===")

    wh = client.webhooks_create(CreateWebhookOptions(
        url="https://webhook.site/your-id",
        events=["screenshot.done"],
        secret="my-signing-secret",
    ))
    print(f"Webhook created: {wh.id}")

    webhooks = client.webhooks_list()
    for w in webhooks:
        print(f"  {w.id} → {w.url}  events={w.events}")

    del_result = client.webhooks_delete(wh.id)
    print("Webhook deleted:", del_result.success)


def keys_demo():
    print("\n=== API Keys ===")

    # List existing (values are masked)
    existing = client.keys_list()
    for k in existing:
        print(f"  {k.name}  {k.key}  last_used={k.last_used}")

    # Create
    new_key = client.keys_create("ci-pipeline")
    print("New key created!")
    print("  Name:", new_key.name)
    print("  Key (save this!):", new_key.key)

    # Delete
    del_result = client.keys_delete(new_key.id)
    print("Key deleted:", del_result.success)


if __name__ == "__main__":
    scheduled_demo()
    webhooks_demo()
    keys_demo()
