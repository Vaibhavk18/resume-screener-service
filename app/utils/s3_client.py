import boto3
import os
import asyncio
from io import BytesIO
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BUCKET = os.getenv("S3_BUCKET")

# Initialize S3 client globally
s3 = boto3.client("s3", region_name=AWS_REGION)


async def upload_resume(file_obj: BytesIO, filename: str, content_type: str = None, folder: str = None) -> str:
    
    if not BUCKET:
        raise ValueError("S3_BUCKET not configured in environment variables")

    key = f"{folder}/{filename}" if folder else filename
    extra_args = {"ContentType": content_type} if content_type else {}

    def _upload():
        try:
            s3.upload_fileobj(file_obj, BUCKET, key, ExtraArgs=extra_args)
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Failed to upload to S3: {e}")

    # Run upload in a non-blocking thread
    await asyncio.to_thread(_upload)

    return f"https://{BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
