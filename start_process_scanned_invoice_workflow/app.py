import json
import os

import boto3

client = boto3.client("stepfunctions")
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]


def lambda_handler(event, context):
    body = json.loads(event["Records"][0]["body"])
    message = json.loads(body["Message"])
    document_location = message["DocumentLocation"]
    bucket_name = document_location["S3Bucket"]
    key = document_location["S3ObjectName"]
    key_split_on_slash = key.split("/")
    join_with_dash = "-".join(key_split_on_slash)
    join_split_on_colon = join_with_dash.split(":")
    job_name = "_".join(join_split_on_colon)
    job_id = message["JobId"]
    status = message["Status"]
    response = client.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        input='{"bucket_name": "'
        + bucket_name
        + '","key": "'
        + key
        + '","job_name": "'
        + job_name
        + '","job_id": "'
        + job_id
        + '","status": "'
        + status
        + '"}',
    )
    return response["executionArn"]
