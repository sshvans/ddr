import boto3
import json
import os
import traceback
import time
from ddr_server import ddr_config

def poll_sqs():
    sqs = boto3.client('sqs')
    s3 = boto3.resource('s3')

    s3bucket = ddr_config.get_config('s3_bucket')
    queueUrl = ddr_config.get_config('sqs_url')

    response = sqs.receive_message(
        QueueUrl=queueUrl
    )

    try:
        messages = response['Messages']
        #    print(messages)

        receiptHandles = [x['ReceiptHandle'] for x in messages]
        msgBodies = [json.loads(x['Body']) for x in messages]

        s3Keys = [x['Records'][0]['s3']['object']['key'] for x in msgBodies]
        print(s3Keys)

        for s3Key in s3Keys:
            s3filename = str(s3Key)
            print(s3filename)
            s3.Bucket(s3bucket).download_file(s3filename, os.path.expanduser('~') + '/' + s3filename)

        for receipt in receiptHandles:
            sqs.delete_message(
                QueueUrl=queueUrl,
                ReceiptHandle=receipt
            )
    except Exception:
        traceback.print_exc()
        print("No messages in sqs")


while True:
    # Run forever, poll queue for new messages, sleeping 100ms in between
    poll_sqs()
    time.sleep(0.1)

    #print(response['Messages'][0]['Body'])
    #print(response['Messages'][0]['Body']['Records'][1])
    #print(response['Messages'][1]['Body'])
    #print(response)