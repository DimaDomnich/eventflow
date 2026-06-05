import boto3
import os
from PIL import Image
import io

S3_BUCKET = os.getenv("S3_BUCKET")
THUMBNAIL_PREFIX = "thumbnails/"
THUMBNAIL_SIZE = (400, 300)

s3 = boto3.client("s3")


def handler(event, context):
    record = event["Records"][0]
    key = record["s3"]["object"]["key"]

    if key.startswith(THUMBNAIL_PREFIX):
        return

    response = s3.get_object(Bucket=S3_BUCKET, Key=key)
    image_data = response["Body"].read()

    image = Image.open(io.BytesIO(image_data))
    image.thumbnail(THUMBNAIL_SIZE)

    buffer = io.BytesIO()
    image.save(buffer, format=image.format or "JPEG")
    buffer.seek(0)

    thumbnail_key = THUMBNAIL_PREFIX + key.split("/")[-1]

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=thumbnail_key,
        Body=buffer,
        ContentType=response["ContentType"],
    )

    return {"statusCode": 200, "thumbnail_key": thumbnail_key}
