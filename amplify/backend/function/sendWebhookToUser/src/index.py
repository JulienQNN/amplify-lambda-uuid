import json
import requests
from io import BytesIO
import boto3

s3_client = boto3.client("s3")
f = BytesIO()


def handler(event, context):
    print("received event:")

    filename = event["Records"][0]["s3"]["object"]["key"]
    bucket = event["Records"][0]["s3"]["bucket"]["name"]

    file = s3_client.get_object(
        Bucket=bucket,
        Key=filename,
    )
    data = file["Body"].read().decode("utf-8")
    dataJSON = json.loads(data)
    url = dataJSON["webhook"]

    payload = json.dumps({"content": str(dataJSON["data"])})

    headers = {
        "Content-Type": "application/json",
    }
    requests.request("POST", url, headers=headers, data=payload)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps("Webhook sent !"),
    }
