import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

lambdaEvent = boto3.client("lambda")
dynamodb = boto3.resource("dynamodb")
s3_client = boto3.client("s3")


table_data = dynamodb.Table(os.environ["STORAGE_DATA_NAME"])
table_user = dynamodb.Table(os.environ["STORAGE_USER_NAME"])

bucket = os.environ["STORAGE_USERDATABUCKET_BUCKETNAME"]


def handler(event, context):
    print("received de levent de sqs")

    response = {}
    user_id = json.loads(event["Records"][0]["body"])["user_id"]
    user_webhook = get_user_webhook(user_id)
    user_data = get_user_data(user_id)

    response["userId"] = user_id
    response["webhook"] = user_webhook
    response["data"] = user_data

    put_object_S3(response)


def get_user_data(user_id):
    response = table_data.query(
        IndexName="userId-index",
        KeyConditionExpression=Key("userId").eq(user_id),
        ProjectionExpression="#data",
        ExpressionAttributeNames={"#data": "data"},
    )

    return response["Items"]


def get_user_webhook(user_id):
    try:
        response = table_user.scan(
            ProjectionExpression="webhook", FilterExpression=Attr("id").eq(user_id)
        )
        return response["Items"][0]["webhook"]

    except:
        return False


def put_object_S3(data):
    s3_client.put_object(
        Body=json.dumps(data),
        Bucket="userdatabucket94653-dev",
        Key=f"data/{data['userId']}/data.json",
    )
