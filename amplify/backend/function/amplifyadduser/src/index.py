import json

from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')

def handler(event, context):
    table = dynamodb.Table('userId-dev')
    print('received AMPLIFY ADD USER event:')
    print(event)

    if event:
        print('ici')
        insert_user(table, event)
        return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('Hello from your new Amplify Python lambda!')
    }

    return {
        'statusCode': 401,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('Could not insert')
    }

def insert_user(table, payload):
    return table.put_item(Item={
      'id': payload.userId,
      'data': payload.data
    })