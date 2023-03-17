import json
import logging
import os
import uuid
import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client("s3")


def handler(event, context):
    try:

        user_id = event["userId"]

        s3_client.put_object(
            Body=json.dumps(event["data"]),
            Bucket="userdatabucket94653-dev",
            Key=f"data/{user_id}/data.json",
        )
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": "userdatabucket94653-dev",
                "Key": f"data/{user_id}/data.json",
            },
            ExpiresIn=3600,
        )

        return url

    except ClientError as e:
        logging.error(e)
        return False
