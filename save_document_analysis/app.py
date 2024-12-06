import copy
import json
import os

import boto3

texttract_client = boto3.client("textract")
s3_client = boto3.client("s3")


def lambda_handler(event, context):
    blocks = []
    analysis = {}
    response = texttract_client.get_document_analysis(JobId=event["job_id"])
    analysis = copy.deepcopy(response)
    while True:
        for block in response["Blocks"]:
            blocks.append(block)
        if "NextToken" not in response.keys():
            break
        next_token = response["NextToken"]
        response = texttract_client.get_document_analysis(
            JobId=event["job_id"], NextToken=next_token
        )
    analysis.pop("NextToken", None)
    analysis["Blocks"] = blocks
    analyses_bucket_name = os.environ["ANALYSES_BUCKET_NAME"]
    analyses_bucket_key = "{}.json".format(event["key"])
    s3_client.put_object(
        Bucket=analyses_bucket_name,
        Key=analyses_bucket_key,
        Body=json.dumps(analysis).encode("utf-8"),
    )
    event["invoice_analyses_bucket_name"] = analyses_bucket_name
    event["invoice_analyses_bucket_key"] = analyses_bucket_key
    return event
