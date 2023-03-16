import json
import boto3

secretmanager = boto3.client("secretsmanager")
lambdaEvent = boto3.client("lambda")
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")


def handler(event, context):
    print("received WEBHOOK event:")
    print(event)
    table = dynamodb.Table("")
    body = json.loads(event["body"])

    if not body["webhook"] or not event["headers"]["x-api-key"]:
        return api_response("NO WEBHOOK OR TOKEN FOUND", 404)

    body = json.loads(event["body"])
    print(body)
    token = event["headers"]["x-api-key"]
    print(token)
    data = body["data"]
    webhook = body["webhook"]

    user_id = get_user_id_in_secret("userSecret", token)
    payload = {"data": data, "userId": user_id}

    # TODO envoyer le payload dans dynamo
    if user_id:
        insert_user(table, payload)

    # TODO ensuite trigger la SQS queue

    return api_response("HELLO LAMBDA", 200)


def insert_user(table, payload):
    return table.put_item(Item={"id": payload["userId"], "data": payload["data"]})


def get_user_id_in_secret(secret_name, secret_key):
    secret_object = secretmanager.get_secret_value(SecretId=secret_name)
    secret_values = json.loads(secret_object["SecretString"])

    for key in secret_values:
        if key == secret_key:
            return secret_values[key]


def api_response(body, status_code):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": body,
    }
