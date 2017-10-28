#! /bin/bash

DDR_ASSETS_BUCKET=$1
ASSETS_BUCKET_REGION=$2
cd lambdas
for file in *.py;
do
    filePart="${file%.*}"
    echo ${filePart}
    zip ${filePart}.zip ${filePart}.py
    aws s3 cp ${filePart}.zip s3://${DDR_ASSETS_BUCKET}/assets/ --region ${ASSETS_BUCKET_REGION}
done
