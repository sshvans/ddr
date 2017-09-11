#! /bin/bash
# To be run on second ec2 server
# nohup /home/ubuntu/ddr/ddr_server/render_images.sh >> /home/ubuntu/render_images.log &
while :
do
  if [ "$(ls -A /efs/archived/*.jpg)" ]; then
    mv /efs/archived/*.jpg /efs/render-processing/
    cd ~/openpose/
    ./build/examples/openpose/openpose.bin --image_dir /efs/render-processing --write_images /efs/rendered/ --no_display
    aws s3 sync /efs/rendered/ s3://ddr-raspi-bucket-1uttsilsw5opt/rendered/
    mv /efs/render-processing/*.jpg /efs/archived-rendered/
    mv /efs/rendered/*.png /efs/archived-rendered/
  fi
  sleep 5
done
