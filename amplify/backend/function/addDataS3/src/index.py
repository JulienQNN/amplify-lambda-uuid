import json
import logging
import os
import uuid
import boto3
from botocore.exceptions import ClientError


def handler(event, context):

    # Upload the file
    s3_client = boto3.client("s3")
    print(event)
    print(json.dumps(event["userId"]))
    print(event["userId"])
    try:
        s3_client.put_object(
            Body=json.dumps(event["data"]),
            Bucket="userdatabucket94653-dev",
            Key="data/" + json.dumps(event["userId"]) + "/data.json",
        )
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": "userdatabucket94653-dev",
                "Key": "data/" + json.dumps(event["userId"]) + "/data.json",
            },
            ExpiresIn=3600,
        )

        return url

    except ClientError as e:
        logging.error(e)
        return False
