import json
import boto3
import os

secretmanager = boto3.client("secretsmanager")
lambdaEvent = boto3.client("lambda")
dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")
table_user = dynamodb.Table(os.environ["STORAGE_USER_NAME"])


def handler(event, context):
    print("received WEBHOOK event:")
    print(event)

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
    send_message_to_sqs(user_id)

    return api_response("HELLO LAMBDA", 200)


expression = "SET list_elm = list_append( if_not_exists(list_elm, :empty), :list_elm)"


def update_user(table_user, key, expression, payload):
    table_user.update_item(Key=key, UpdateExpression=expression)


def get_user_id_in_secret(secret_name, secret_key):
    secret_object = secretmanager.get_secret_value(SecretId=secret_name)
    secret_values = json.loads(secret_object["SecretString"])

    for key in secret_values:
        if key == secret_key:
            return secret_values[key]


def send_message_to_sqs(user_id):
    sqs.send_message(
        QueueUrl="https://sqs.eu-west-1.amazonaws.com/554097515570/TriggerLambda",
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
