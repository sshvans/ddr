import boto3
import json
import decimal
import datetime
import traceback
from boto3.dynamodb.conditions import Key, Attr
from ddr_server import ddr_config
import time

class DecimalEncoder(json.JSONEncoder):
    # Helper class to convert a DynamoDB item to JSON.
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
ddbclient = boto3.client('dynamodb', region_name='us-west-2')

score_table = ddr_config.get_config('ddr_score_table')
images_table = ddr_config.get_config('ddr_images_table')
rendered_table = ddr_config.get_config('ddr_rendered_table')


def create_table(table_name, partition_key, sort_key):
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': partition_key, #'score_id',
                'KeyType': 'HASH'  #Partition key
            },
            {
                'AttributeName': sort_key, #'score_ts',
                'KeyType': 'RANGE'  #Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': partition_key, #'score_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': sort_key, #'score_ts',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    print("Table status:", table.table_status)


def check_or_create_table(table_name, partition_key, sort_key):
    try:
        response = ddbclient.describe_table(TableName = table_name)
        print(str(response))
    except:
        traceback.print_exc()
        print("Table " + table_name + " does not exist, creating...")
        create_table(table_name, partition_key, sort_key)


def setup_ddb_tables():
    check_or_create_table(score_table, 'score_id', 'score_ts')
    check_or_create_table(images_table, 'file_id', 'file_ts')
    check_or_create_table(rendered_table, 'file_id', 'file_ts')


def put_score(score_result):
    #[average group score, total group score, number of people, array of individual scores]
    people_scores = [decimal.Decimal(str(x)) for x in score_result[3]]
    table = dynamodb.Table(score_table)
    response = table.put_item(
        Item={
            'score_id': 'DUMMY',
            'score_ts': datetime.datetime.now().isoformat(),
            'group_avg': decimal.Decimal(str(score_result[0])),
            'group_total': decimal.Decimal(str(score_result[1])),
            'num_people': decimal.Decimal(str(score_result[2])),
            'people_scores': people_scores,
            'ttl': long(time.time() + 900)
        }
    )

    print("PutItem succeeded")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))


def put_files(file_ts):
    table = dynamodb.Table(images_table)
    response = table.put_item(
        Item={
            'file_id': 'DUMMY',
            'file_ts': file_ts, #datetime.datetime.now().isoformat(),
            'file_name': 'image' + file_ts + '.jpg',
            'ttl': long(time.time() + 900)
        }
    )


def get_last_score(last_result):
    table = dynamodb.Table(score_table)
    last_key = last_result['lastEvaluatedKey']
    if not last_key:
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


def get_next_two_files(last_evaluated_key):
    table = dynamodb.Table(images_table)
    #LastEvaluatedKey
    db_res = table.query(
        KeyConditionExpression=Key('file_id').eq('DUMMY'),
        Limit=2,
        ScanIndexForward=True,
        ExclusiveStartKey=last_evaluated_key
    )
    #print(db_res)
    return {
        'files': [x['file_ts'] for x in db_res['Items']],
        'lastEvaluatedKey': db_res.get('LastEvaluatedKey', None)
    }


def get_first_last_file(is_first):
    table = dynamodb.Table(images_table)
    db_res = table.query(
        KeyConditionExpression=Key('file_id').eq('DUMMY'),
        Limit=1,
        ScanIndexForward=is_first
    )
    #print(db_res)
    return {
        'files': [x['file_ts'] for x in db_res['Items']],
        'lastEvaluatedKey': db_res['LastEvaluatedKey']
    }


