import os

import boto3

s3_client = boto3.client("s3")


def lambda_handler(event, context):
    bucket_name = event["bucket_name"]
    key = event["key"]
    source = {"Bucket": bucket_name, "Key": key}
    archive_bucket_name = os.environ["ARCHIVE_BUCKET_NAME"]
    s3_client.copy(source, archive_bucket_name, key)
    s3_client.delete_object(Bucket=bucket_name, Key=key)
    return event
