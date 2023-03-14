import json
import boto3
import os
from botocore.exceptions import ClientError
import uuid
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')


def handler(event, context):
    table = dynamodb.Table('user-dev')
    #body = json.loads(event['body'])
    body = event['body']
    print(body)
    response = get_user(table, body)
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': response
    }


def get_user(table, body):
    print("==== get user ====")
    try:
        data = scan(table, filter_expression=Attr(
            'lastname').eq(body['lastname']), projection='firstname, lastname, age')

        if (data):
            return 'Oui il existre'

        return 'Non il existe pas'

    except KeyError:
        data = 'User not found'

    return data




def scan(table, filter_expression, projection):
    data = []
    response = {}
    
    while True:
        kwargs = {
            'FilterExpression': filter_expression,
            'ProjectionExpression': projection
        }

        last = response.get('LastEvaluatedKey')

        if response.get('LastEvaluatedKey'):
            kwargs['ExclusiveStartKey'] = last

        response = table.scan(**kwargs)

        data.extend(response['Items'])

        if 'LastEvaluatedKey' not in response:
            break

    return data
