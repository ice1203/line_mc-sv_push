# -*- coding: utf-8 -*-
import boto3
import os
import sys
import re
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'linebotAPI'))

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, JoinEvent, TextMessage, TextSendMessage,
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2_instanceid = [ os.getenv('EC2_INSTANCEID', None) ]

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    logger.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
#dynamodb = boto3.resource('dynamodb')
#mtable    = dynamodb.Table('managed-table')

#def get_servicestat(instanceid):
#    try:
#        response = mtable.get_item(
#            Key={
#                'id': instanceid ,
#                'managed-item': "minecraft-sv-status"
#            }
#        )
#    except ClientError as e:
#        print(e.response['Error']['Message'])
#    else:
#        #item = response['Item']
#        print("dynamodb GetItem succeeded:")
#        #print(json.dumps(item, indent=4, cls=DecimalEncoder))
#        return response['Item']
#
def lambda_handler(event, context):
    ok_json = {"isBase64Encoded": False,
               "statusCode": 200,
               "headers": {},
               "body": ""}
    error_json = {"isBase64Encoded": False,
                  "statusCode": 403,
                  "headers": {},
                  "body": "Error"}
    #print(event["Records"])
    for record in event["Records"]:
        try:
            new_stat = record["dynamodb"]["NewImage"]["service_stat"]["S"]
            old_stat = record["dynamodb"]["OldImage"]["service_stat"]["S"]
            if not old_stat == new_stat and 'サービス中（ログイン可）' in new_stat:
                print("loginOK")
                line_roomid = record["dynamodb"]["NewImage"]["line_rid"]["S"]
                try:
                    line_bot_api.push_message(line_roomid, TextSendMessage(text='ば、爆発しちゃうっっ！！（意訳：ログイン可能になりました'))
                    return ok_json
                except LineBotApiError as e:
                    logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
                    for m in e.error.details:
                        logger.error("  %s: %s" % (m.property, m.message))
                    return error_json
                except InvalidSignatureError:
                    return error_json
            else:
                return ok_json
        except KeyError as e:
            print('I got a KeyError')
        except IndexError as e:
            print('I got an IndexError')

    return ok_json
