"""examples/async_example.py – SnapAPI v2 Python SDK (async)
Requires: pip install snapapi[async]
"""
import asyncio
import os

from snapapi import AsyncSnapAPI, ScrapeOptions, ExtractOptions, CreateScheduledOptions, CreateWebhookOptions


async def main():
    async with AsyncSnapAPI(api_key=os.environ.get("SNAPAPI_KEY", "sk_live_YOUR_KEY")) as client:

        # Screenshot
        print("Taking async screenshot…")
        buf = await client.screenshot(
            url="https://example.com",
            dark_mode=True,
            full_page=True,
            block_ads=True,
        )
        open("async_shot.png", "wb").write(buf)
        print("Saved async_shot.png")

        # Store in cloud
        stored = await client.screenshot(
            url="https://example.com",
            storage={"destination": "snapapi"},
        )
        print("Stored:", stored)

        # Scrape
        result = await client.scrape(ScrapeOptions(
            url="https://news.ycombinator.com",
            type="text",
            wait_ms=500,
        ))
        print("Scraped:", result.results[0].data[:200])

        # Extract
        ext = await client.extract(ExtractOptions(
            url="https://en.wikipedia.org/wiki/Screenshot",
            type="markdown",
            clean_output=True,
            max_length=2000,
        ))
        print("Extracted (first 300):", str(ext.content)[:300])

        # Storage usage
        usage = await client.storage_get_usage()
        print(f"Storage: {usage.used_formatted} / {usage.limit_formatted}")

        # List storage files
        listing = await client.storage_list_files(limit=5)
        print(f"Files: {len(listing.files)}")

        # Scheduled screenshots
        job = await client.scheduled_create(CreateScheduledOptions(
            url="https://example.com",
            cron_expression="0 9 * * *",
        ))
        print("Scheduled job:", job.id)
        jobs = await client.scheduled_list()
        print("All jobs:", [j.id for j in jobs])
        await client.scheduled_delete(job.id)

        # Webhooks
        wh = await client.webhooks_create(CreateWebhookOptions(
            url="https://webhook.site/your-id",
            events=["screenshot.done"],
        ))
        print("Webhook:", wh.id)
        await client.webhooks_delete(wh.id)

        # API Keys
        keys = await client.keys_list()
        print("Keys:", [k.name for k in keys])
        new_key = await client.keys_create("async-example")
        print("Created key:", new_key.name)
        await client.keys_delete(new_key.id)


if __name__ == "__main__":
    asyncio.run(main())
