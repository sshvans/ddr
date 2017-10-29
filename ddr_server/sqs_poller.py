import boto3
import json
import os
import traceback
import time
import sys
import zmq
from heapq import *
from multiprocessing import Pool
from ddr_server import ddr_config
from ddr_server import ddb_util

s3bucket = ddr_config.get_config('s3_bucket')
s3region = ddr_config.get_config('s3_bucket_region')
queueUrl = ddr_config.get_config('sqs_url')
numServers = int(ddr_config.get_config('num_op_servers'))
processed_table = ddr_config.get_config('ddr_processed_table')



def poll_sqs():
    s3bucket = ddr_config.get_config('s3_bucket')
    s3region = ddr_config.get_config('s3_bucket_region')
    queueUrl = ddr_config.get_config('sqs_url')
    numServers = int(ddr_config.get_config('num_op_servers'))
    processed_table = ddr_config.get_config('ddr_processed_table')

    sqs = boto3.client('sqs', region_name=s3region)
    s3 = boto3.resource('s3', region_name=s3region)
    rekognition = boto3.client('rekognition', region_name=s3region)

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

        pool = Pool(2)

        fileQueue = []

        serverIndex = 0
        for s3Key in s3Keys:
            s3filename = str(s3Key)
            start_time = time.time()
            print(s3filename)
            lastSlashIndex = s3filename.rfind('/')
            filename = s3filename[lastSlashIndex + 1: len(s3filename)]
            serverIndex += 1

            # result = processOpenpose(s3, s3bucket, s3filename, filename, serverIndex, numServers)
            # rekResponse = processRekognition(rekognition, s3bucket, s3filename)
            opAsync = pool.apply_async(processOpenpose, [s3bucket, s3filename, filename, serverIndex, numServers])
            rekAsync = pool.apply_async(processRekognition,[s3bucket, s3filename])

            result = opAsync.get(timeout=10)
            rekResponse = rekAsync.get(timeout=10)

            elapsed_time = time.time() - start_time

            print("Processed s3 file in: " + str(elapsed_time))

            pool.close()
            pool.join()

            if result == "Done.":
                print("Rekognition response\n" + str(rekResponse))
                ddb_util.log_processed(filename, processed_table, rekResponse)



        for receipt in receiptHandles:
            sqs.delete_message(
                QueueUrl=queueUrl,
                ReceiptHandle=receipt
            )
    except Exception:
        # traceback.print_exc()
        print("No messages in sqs")


def processRekognition(s3bucket, s3filename):

    start_time = time.time()
    rekognition = boto3.client('rekognition', region_name=s3region)
    response = rekognition.detect_faces(Image={'S3Object':{'Bucket':s3bucket,'Name':s3filename}},Attributes=['ALL'])
    emotions = []
    smiles = []
    rek_response = {}

    for faceDetail in response['FaceDetails']:
        emotions.append(faceDetail['Emotions'])
        smiles.append(faceDetail['Smile'])

        #print('The detected face is between ' + str(faceDetail['AgeRange']['Low'])
        #      + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')
        #print('Here are the other attributes:')
        #print(json.dumps(faceDetail, indent=4, sort_keys=True))

    rek_response['Emotions'] = emotions
    rek_response['Smiles'] = smiles

    elapsed_time = time.time() - start_time
    print("Processed rekognition in: " + str(elapsed_time))
    return rek_response


def processOpenpose(s3bucket, s3filename, filename, serverIndex, numServers):

    start_time = time.time()
    s3 = boto3.resource('s3', region_name=s3region)

    s3.Bucket(s3bucket).download_file(s3filename, os.path.expanduser('~') + '/' + s3filename)
    result = processImage(filename, 5555 + serverIndex % numServers)
    print("Server result: " + str(result))
    if result == "Done.":
        # heappush(fileQueue, filename)
        rendered_file = filename.replace(".jpg", "_rendered.png")
        s3.Bucket(s3bucket).upload_file(os.path.expanduser('~') + '/rendered/' + rendered_file,
                                       'rendered/' + rendered_file)

    elapsed_time = time.time() - start_time
    print("Processed openpose in: " + str(elapsed_time))

    return result



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

