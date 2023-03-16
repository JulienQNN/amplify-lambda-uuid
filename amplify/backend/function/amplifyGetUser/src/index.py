import json
import boto3
from botocore.exceptions import ClientError
import uuid
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
secretmanager = boto3.client("secretsmanager")


def handler(event, context):
    table = dynamodb.Table("user-dev")
    body = json.loads(event["body"])
    # body = event['body']
    response = get_user(table, body)

    if response:
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": response,
        }


def get_user(table, body):
    try:
        data = scan(
            table,
            filter_expression=Attr("lastname").eq(body["lastname"]),
            projection="firstname, lastname, age, id",
        )

        if data:
            user = data[0]
            secret = get_secret("userSecret", user["id"])

            return secret
        else:
            id = insert_user(table, body)
            secret = create_secret("userSecret", id)

            return secret

    except KeyError:
        data = "User not found"


def insert_user(table, body):

    id = str(uuid.uuid4())

    table.put_item(
        Item={
            "id": id,
            "age": str(body["age"]),
            "firstname": str(body["firstname"]),
            "lastname": str(body["lastname"]),
        }
    )

    return id


def create_secret(secret_name, id):

    secret_object = secretmanager.get_secret_value(SecretId=secret_name)

    secretuuid4 = str(uuid.uuid4())

    if secret_object:
        secret_global_object = json.loads(secret_object["SecretString"])
        secret_global_object[secretuuid4] = id
        secret = json.dumps(secret_global_object)

        secretmanager.put_secret_value(
            SecretId="userSecret",
            SecretString=secret,
        )

    else:
        secretmanager.create_secret(
            Name="userSecret", SecretString=json.dumps({secret: id})
        )
    return secretuuid4


def get_secret(secret_name, secret_key):

    secret_object = secretmanager.get_secret_value(SecretId=secret_name)

    secret_values = json.loads(secret_object["SecretString"])

    for key in secret_values:
        if secret_values[key] == secret_key:
            return key


def scan(table, filter_expression, projection):
    data = []
    response = {}

    while True:
        kwargs = {
            "FilterExpression": filter_expression,
            "ProjectionExpression": projection,
        }

        last = response.get("LastEvaluatedKey")

        if response.get("LastEvaluatedKey"):
            kwargs["ExclusiveStartKey"] = last

        response = table.scan(**kwargs)

        data.extend(response["Items"])

        if "LastEvaluatedKey" not in response:
            break

    return data
