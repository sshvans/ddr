# aws rekognition detect-faces
# --image
# '{"S3Object":{"Bucket":"ddr-raspi-bucket-1uttsilsw5opt","Name":"images/image2017-09-22T15_51_08.401422.jpg"}}'
# --attributes ALL --region us-west-2

import boto3
import json

if __name__ == "__main__":
    fileName='images/image2017-09-22T15_51_08.401422.jpg'
    bucket='ddr-raspi-bucket-1uttsilsw5opt'
    client=boto3.client('rekognition', region_name='us-west-2')

    response = client.detect_faces(Image={'S3Object':{'Bucket':bucket,'Name':fileName}},Attributes=['ALL'])

    print('Detected faces for ' + fileName)
    i = 0

    emotions = []
    smiles = []
    rek_response = {}

    for faceDetail in response['FaceDetails']:
        print('Detected person: ' + str(i))
        i += 1
        #print("Emotion: ")
        emotions.append(faceDetail['Emotions'])
        #print(json.dumps(faceDetail['Emotions']))

        #print("Smile: ")
        #print(json.dumps(faceDetail['Smile']))
        smiles.append(faceDetail['Smile'])
        #print('The detected face is between ' + str(faceDetail['AgeRange']['Low'])
        #      + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')
        #print('Here are the other attributes:')
        #print(json.dumps(faceDetail, indent=4, sort_keys=True))

    rek_response['Emotions'] = emotions
    rek_response['Smiles'] = smiles

    #print("Smiles\n" + json.dumps(smiles, indent=4, sort_keys=True))
    #print("Emotions\n" + json.dumps(emotions, indent=4, sort_keys=True))
    print("Rek Response\n" + json.dumps(rek_response, indent=4, sort_keys=True))

