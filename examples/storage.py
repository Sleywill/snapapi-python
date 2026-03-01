"""examples/storage.py – SnapAPI v2 Python SDK"""
import os
from snapapi import SnapAPI, S3Config

client = SnapAPI(api_key=os.environ.get("SNAPAPI_KEY", "sk_live_YOUR_KEY"))


def main():
    # 1. Check storage usage
    usage = client.storage_get_usage()
    print(f"Storage: {usage.used_formatted} / {usage.limit_formatted} ({usage.percentage}%)")

    # 2. Take a screenshot and store it
    stored = client.screenshot(
        url="https://example.com",
        storage={"destination": "snapapi", "format": "png"},
    )
    file_id = stored["id"]
    print("Stored file ID:", file_id)
    print("Public URL:", stored["url"])

    # 3. List stored files
    listing = client.storage_list_files(limit=10, offset=0)
    print(f"You have {len(listing.files)} files stored:")
    for f in listing.files:
        print(f"  - {f.id}  {f.url}")

    # 4. Get a specific file
    if listing.files:
        file = client.storage_get_file(listing.files[0].id)
        print("File details:", file)

    # 5. Delete the file we uploaded
    del_result = client.storage_delete_file(file_id)
    print("Deleted:", del_result.success)

    # 6. Configure custom S3 bucket
    client.storage_configure_s3(S3Config(
        s3_bucket="my-screenshots",
        s3_region="us-east-1",
        s3_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "AKIA..."),
        s3_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "secret"),
    ))

    # 7. Test the S3 connection
    test = client.storage_test_s3()
    print("S3 test:", "✅ OK" if test.success else "❌ Failed", test.message)


if __name__ == "__main__":
    main()
