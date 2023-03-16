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
    print(event)
    user_id = json.loads(event["Records"][0]["body"])["user_id"]
    print("user_id", user_id)
    user_webhook = get_user_webhook(user_id)
    user_data = get_user_data(user_id)

    response["userId"] = user_id
    response["webhook"] = user_webhook
    response["data"] = user_data

    print(response)

    # conn = http.client.HTTPSConnection("discord.com")
    # payload = json.dumps({"content": "Hey voici le contenu du Webhook!"})
    # headers = {
    #     "Content-Type": "application/json",
    # }
    # conn.request(
    #     "POST",
    #     "/api/webhooks/1085859153853038632/fjypzqJdP16m5Dqdq7nr1RZfCdOQHZqNw77GYqjVjLfgj_xSw6afW9H1BQUELZ1X6_x3",
    #     payload,
    #     headers,
    # )
    # res = conn.getresponse()
    # data = res.read()

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps("Hello from your new Amplify Python lambda!"),
    }


def get_user_data(user_id):
    response = table_data.query(
        IndexName="user_id__",
        KeyConditionExpression=Key("user_id").eq(user_id),
        ProjectionExpression="#data",
        ExpressionAttributeNames={"#data": "data"},
    )
    print(response)

    return response["Items"]


def get_user_webhook(user_id):
    try:
        response = table_user.scan(
            ProjectionExpression="webhook", FilterExpression=Attr("id").eq(user_id)
        )
        return response["Items"][0]["webhook"]

    except:
        return False
