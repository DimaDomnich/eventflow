import os
import uuid

from app.extensions import get_s3_client


def upload_file_to_s3(file, folder):
    s3 = get_s3_client()

    bucket = os.getenv("S3_BUCKET")
    key = f"{folder}/{uuid.uuid4()}-{file.filename}"

    s3.upload_fileobj(file, bucket, key, ExtraArgs={"ContentType": file.content_type})

    return f"https://{bucket}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{key}"
