#!/usr/bin/env python

# This code is simply for demo and needs to be replaced

from picamera import PiCamera
from time import sleep

import boto3
import yaml

s3 = boto3.client('s3')

with open("ddr_camera.props", 'r') as propsfile:
    props = yaml.load(propsfile)

bucket = props.get('s3_bucket')
rotation = props.get('rotation', 0)
captures_per_second = props.get('captures_per_second', 10)

camera = PiCamera()
camera.rotation = rotation

camera.start_preview()

# camera warmup
sleep(2)

print 'camera started'

for i in range(5):
    filename='image%s.jpg' % i
    pathname='/home/pi/images/' + filename
    camera.capture(pathname)
    sleep(1/captures_per_second)
    data = open(pathname, 'rb')
    s3.upload_file(pathname, bucket, filename)

camera.stop_preview()
print 'camera stopped'
