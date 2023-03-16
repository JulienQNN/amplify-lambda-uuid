import http.client
import json


def handler(event, context):
    print("received de levent de sqs")
    print(event)

    conn = http.client.HTTPSConnection("discord.com")
    payload = json.dumps({"content": "Hey voici le contenu du Webhook!"})
    headers = {
        "Content-Type": "application/json",
    }
    conn.request(
        "POST",
        "/api/webhooks/1085859153853038632/fjypzqJdP16m5Dqdq7nr1RZfCdOQHZqNw77GYqjVjLfgj_xSw6afW9H1BQUELZ1X6_x3",
        payload,
        headers,
    )
    res = conn.getresponse()
    data = res.read()
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps("Hello from your new Amplify Python lambda!"),
    }
