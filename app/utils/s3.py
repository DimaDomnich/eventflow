import os
import uuid

from app.extensions import get_s3_client
from urllib.parse import urlparse


def extract_s3_key(url: str) -> str:
    path = urlparse(url).path
    return path.lstrip("/")


def upload_file_to_s3(file, folder):
    s3 = get_s3_client()

    bucket = os.getenv("S3_BUCKET")
    key = f"{folder}/{uuid.uuid4()}-{file.filename}"

    s3.upload_fileobj(file, bucket, key, ExtraArgs={"ContentType": file.content_type})

    return f"https://{bucket}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{key}"


def remove_file_from_s3(file_path):
    s3 = get_s3_client()
    bucket = os.getenv("S3_BUCKET")

    s3.delete_object(Bucket=bucket, Key=file_path)

    filename = file_path.split("/")[-1]
    s3.delete_object(Bucket=bucket, Key=f"thumbnails/{filename}")
