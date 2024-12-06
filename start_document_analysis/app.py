import os

import boto3

client = boto3.client("textract")
SNS_TOPIC = os.environ["DOCUMENT_ANALYIS_COMPLETED_SNS_TOPIC_ARN"]
ROLE_ARN = os.environ["TEXTRACT_PUBLISH_TO_SNS_ROLE_ARN"]


def lambda_handler(event, context):
    s3 = event["Records"][0]["s3"]
    bucket_name = s3["bucket"]["name"]
    key = s3["object"]["key"]
    document_location = {"S3Object": {"Bucket": bucket_name, "Name": key}}
    response = client.start_document_analysis(
        DocumentLocation=document_location,
        FeatureTypes=["TABLES", "FORMS"],
        NotificationChannel={
            "SNSTopicArn": SNS_TOPIC,
            "RoleArn": ROLE_ARN,
        },
    )
    event["job_id"] = response["JobId"]
    event["bucket_name"] = bucket_name
    event["key"] = key
    return event
