import json
import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid

secretmanager = boto3.client("secretsmanager")
lambdaEvent = boto3.client("lambda")
dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")

table_data = dynamodb.Table(os.environ["STORAGE_DATA_NAME"])
table_user = dynamodb.Table(os.environ["STORAGE_USER_NAME"])


SQS_URL = "https://sqs.eu-west-1.amazonaws.com/554097515570/TriggerLambda"


def handler(event, context):

    if not event["body"]:
        return api_response("Data missing", 404)

    body = json.loads(event["body"])

    if not body["webhook"] or not event["headers"]["x-api-key"]:
        return api_response("Webhook or Token not found", 404)

    data = body["data"]
    token = event["headers"]["x-api-key"]
    webhook = body["webhook"]

    user_id = get_user_id_in_secret("userSecret", token)

    if not user_id:
        return api_response("no user_id in secret", 401)

    payload = {"data": data, "userId": user_id, "webhook": webhook}

    insertion_new_data = insert_new_data(table_data, user_id, data)
    update_user_webhook = update_user(table_user, payload)

    if insertion_new_data and update_user_webhook:
        api_response("all good", 200)
    else:
        api_response("error during data insert", 500)

    send_message_to_sqs(user_id)


def update_user(table_user, payload):
    expression = "SET webhook = :webhook"
    values = {":webhook": payload["webhook"]}

    sk = get_user_sk(table_user, payload["userId"])

    try:
        table_user.update_item(
            Key={"id": payload["userId"], "lastname": sk},
            UpdateExpression=expression,
            ExpressionAttributeValues=values,
        )
        return True
    except:
        return False


def insert_new_data(table_data, user_id, data):
    obj = {"id": str(uuid.uuid4()), "userId": user_id, "data": data}
    try:
        table_data.put_item(Item=obj)
        return True
    except:
        return False


def get_user_sk(table_user, user_id):
    response = table_user.query(
        KeyConditionExpression=Key("id").eq(user_id),
        ProjectionExpression="lastname",
    )
    return response["Items"][0]["lastname"]


def get_user_id_in_secret(secret_name, secret_key):
    secret_object = secretmanager.get_secret_value(SecretId=secret_name)
    secret_values = json.loads(secret_object["SecretString"])

    for key in secret_values:
        if key == secret_key:
            return secret_values[key]


def send_message_to_sqs(user_id):
    sqs.send_message(
        QueueUrl=SQS_URL,
        MessageBody=json.dumps({"user_id": user_id}),
    )


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
