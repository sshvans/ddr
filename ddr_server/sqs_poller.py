import boto3
import json
import os
import traceback
import time
import sys
import zmq
from heapq import *
from ddr_server import ddr_config
from ddr_server import ddb_util


def poll_sqs():
    sqs = boto3.client('sqs')
    s3 = boto3.resource('s3')

    s3bucket = ddr_config.get_config('s3_bucket')
    queueUrl = ddr_config.get_config('sqs_url')
    numServers = int(ddr_config.get_config('num_op_servers'))
    processed_table = ddr_config.get_config('ddr_processed_table')

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

        fileQueue = []

        serverIndex = 0
        for s3Key in s3Keys:
            s3filename = str(s3Key)
            print(s3filename)
            lastSlashIndex = s3filename.rfind('/')
            filename = s3filename[lastSlashIndex + 1: len(s3filename)]
            serverIndex += 1
            s3.Bucket(s3bucket).download_file(s3filename, os.path.expanduser('~') + '/' + s3filename)
            result = processImage(filename, 5555 + serverIndex % numServers)
            if result == "Done.":
                # heappush(fileQueue, filename)
                ddb_util.log_processed(filename, processed_table)

        for receipt in receiptHandles:
            sqs.delete_message(
                QueueUrl=queueUrl,
                ReceiptHandle=receipt
            )
    except Exception:
        # traceback.print_exc()
        print("No messages in sqs")


def processImage(filename, serverIndex):
    context = zmq.Context()

    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:" + str(serverIndex))

    #  Send request
    socket.send(filename.encode())

    #  Get the reply.
    message = socket.recv()
    return message


def main(argv):
    while True:
        # Run forever, poll queue for new messages, sleeping 100ms in between
        poll_sqs()
        time.sleep(0.1)

        #print(response['Messages'][0]['Body'])
        #print(response['Messages'][0]['Body']['Records'][1])
        #print(response['Messages'][1]['Body'])
        #print(response)


if __name__ == '__main__':
    main(sys.argv[1:])

