import logging
import boto3
from botocore.exceptions import ClientError
import json
import simplejson
import decimal
import math
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
table_name = 'ddr_score'
pk = 'pk'


def get_last_score():
    table = dynamodb.Table(table_name)
    db_res = table.query(KeyConditionExpression=Key('score_id').eq('DUMMY'),Limit=1,ScanIndexForward=False)
    return str(db_res['Items'][0]['group_total'])


def get_next_score(last_result):
    table = dynamodb.Table(table_name)
    last_key = last_result['lastEvaluatedKey']
    if (not last_key) or (last_key == 'null'):
        db_res = table.query(KeyConditionExpression=Key('score_id').eq('DUMMY'),Limit=1,ScanIndexForward=False)
    else:
        db_res = table.query(
            KeyConditionExpression=Key('score_id').eq('DUMMY'),
            Limit=1,
            ScanIndexForward=True,
            ExclusiveStartKey=last_key
        )

    if len(db_res['Items']) > 0:
        score = str(db_res['Items'][0]['group_total'])
    else:
        score = last_result['score']

    return {
        'score': score,
        'lastEvaluatedKey': db_res.get('LastEvaluatedKey', None)
    }


# Lambda function handler method
def get_score(event, context):
    logger.info('got event {}'.format(event))
    logger.info('lek: {}'.format(event['queryStringParameters']['lek']))

    # Get score
    table = dynamodb.Table(table_name)

    try:
        lek = json.loads(event['queryStringParameters']['lek'])
    except:
        lek = None

    last_score = {'score': None, 'lastEvaluatedKey': lek}
    fetched_score = get_next_score(last_score)
    #transformed_score = math.tanh(float(fetched_score) / 50.0) * 100.0
    transformed_score = fetched_score

    logger.debug('score is {}'.format(transformed_score))

    status = transformed_score

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST"
        },
        "body": json.dumps(status, indent=4, cls=DecimalEncoder)
    }

    return response


class DecimalEncoder(json.JSONEncoder):
    # Helper class to convert a DynamoDB item to JSON.
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
