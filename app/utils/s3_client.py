import boto3, os,asyncio
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION",))
BUCKET = os.getenv("S3_BUCKET")

async def upload_resume(file_obj, filename, content_type=None):
    extra_args = {"ContentType": content_type} if content_type else {}

    def _upload():
        s3.upload_fileobj(file_obj, BUCKET, filename, ExtraArgs=extra_args)
    await asyncio.to_thread(_upload)
    return f"https://{BUCKET}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{filename}"
