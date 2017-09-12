#! /bin/bash

S3_BUCKET=$( cat ddr_config.props | grep s3_bucket | cut -d':' -f2 | tr -d ' ' )
echo ${S3_BUCKET}
API_URL=$( cat ddr_config.props | grep api_url | cut -d':' -f2- | tr -d ' ' )
echo ${API_URL}
S3_WEBAPP_BUCKET=$( cat ddr_config.props | grep s3_webapp_bucket | cut -d':' -f2 | tr -d ' ' )
echo ${S3_WEBAPP_BUCKET}

cd scoreboard-web-app

for html_file in *.html;
do
sed -i '' "s/S3_BUCKET_TOKEN/${S3_BUCKET}/g" ${html_file}
sed -i '' "s/API_URL_TOKEN/${API_URL}/g" ${html_file}
done

aws s3 sync . s3://${S3_WEBAPP_BUCKET}/