#! /bin/bash

S3_WEBAPP_BUCKET=$( cat ddr_config.props | grep s3_webapp_bucket | cut -d':' -f2 | tr -d ' ' )
echo ${S3_WEBAPP_BUCKET}

python deploy_webapp.py

cd scoreboard-web-app
aws s3 sync . s3://${S3_WEBAPP_BUCKET}/

for html_file in *.html;
do
git checkout ${html_file}
done

for js_file in *.js;
do
git checkout ${js_file}
done