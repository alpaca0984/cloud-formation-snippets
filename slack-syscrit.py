import os
import json
import logging
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

Slack_Webhook_URL = os.environ['SLACK_WEBHOOK_URL']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Event: " + str(event))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info("Message: " + str(message))

    NewStateValue = message['NewStateValue']
    NewStateReason = message['NewStateReason']
    AlarmName = message['AlarmName']
    StateChangeTime = (datetime.strptime(message['StateChangeTime'][:-9], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=9)).strftime("%Y/%m/%d %H: %M :%S")
    SlackText = "[" + NewStateValue + "] " + AlarmName
    SlackAttachments = message['AlarmDescription'] + "\n" + message['NewStateReason'] + "\n" + StateChangeTime

    color = "danger"
    icon = ":scream:"
    if NewStateValue == "OK":
        color = "good"
        icon = ":wink:"

    slack_message = {
        'username': "AWS CloudWatch Alarm",
        'text': SlackText,
        'icon_emoji': icon,
        'attachments': [
            {
                "color": color,
                "text": SlackAttachments
            }
        ]
    }

    req = Request(Slack_Webhook_URL, json.dumps(slack_message).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", Slack_Webhook_URL)
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
