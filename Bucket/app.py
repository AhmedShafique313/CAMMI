import boto3
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Documents\CAMMI\.env")

client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
)

def list_buckets(s3):
    response = s3.list_buckets()
    print("\nYour S3 Buckets:")
    for bucket in response['Buckets']:
        print(f" - {bucket['Name']}")

def download_full_bucket(client):
    bucket_name = input("\nEnter the bucket name to download: ").strip()
    local_folder = input("Enter the local directory to save the bucket content (e.g., ./downloads): ").strip()

    os.makedirs(local_folder, exist_ok=True)

    paginator = client.get_paginator('list_objects_v2')
    print(f"\nListing and downloading files from bucket: {bucket_name}...\n")

    try:
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                s3_key = obj['Key']

                # Skip folder placeholders (keys ending with '/')
                if s3_key.endswith('/'):
                    continue
                local_file_path = os.path.join(local_folder, s3_key)
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                print(f"Downloading: {s3_key}")
                client.download_file(bucket_name, s3_key, local_file_path)

        print(f"\n All files from bucket '{bucket_name}' have been downloaded to '{local_folder}'")
    except Exception as e:
        print(f"\n AWS Error: {e}")

if __name__ == "__main__":
    list_buckets(client)
    download_full_bucket(client)