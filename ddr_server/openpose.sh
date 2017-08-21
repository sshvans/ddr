#! /bin/bash
mv ~/images/*.jpg ~/images-processed/
cd ~/openpose/
./build/examples/openpose/openpose.bin --image_dir ~/images-processed --write_keypoint_json ~/json/ --no_display
./build/examples/openpose/openpose.bin --image_dir ~/images-processed --write_images ~/rendered/ --no_display
aws s3 sync ~/json/ s3://ddr-raspi-bucket-1uttsilsw5opt/json/
aws s3 sync ~/rendered/ s3://ddr-raspi-bucket-1uttsilsw5opt/rendered/
mv ~/json/*.json ~/archived/
mv ~/rendered/*.png ~/archived/
