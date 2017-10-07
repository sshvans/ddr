# End-to-end Testing instructions

## Raspberry PI
* Follow instructions in ddr_raspi/README.md
* It will create a S3 bucket
* See instructions in section: *Run ddr_camera.py*

## S3/SQS Setup (to be automated)
* Create a SQS queue in the region (us-west-2)
* For the S3 bucket created above, enable event notifications for put item for images/ prefix to be sent to SQS 

## Openpose EC2 Server
### Configure ddr_config.props
  * ddr_score_table: ddr_score (leave as is)
  * ddr_images_table: ddr_images (leave as is)
  * s3_bucket: ddr-raspi-bucket-1uttsilsw5opt **(change this)**
  * sqs_url: https://us-west-2.queue.amazonaws.com/910000848896/ddr-messages **(change this)**
### Run SQS Poller (infinite loop)
```bash
cd ~/ddr/
git pull
screen -S sqs
python -m ddr_server.sqs_poller
```  
Exit the screen: `Ctrl-A`, `Ctrl-D`

### Run DDR Runner
 ```bash
cd ~/ddr
screen -S ddr
python -m ddr_server.ddr_runner
```
Exit the screen: `Ctrl-A`, `Ctrl-D`

To re-attach the screen, you can do `screen -r sqs, screen -r ddr-test`

## Lambda + API Gateway
* Use the checked in get_score.py to re-build the archive and upload as a lambda
* Make a API gateway front-end for it.
* Ensure CORS is enabled on the API gateway

## Scoreboard web app
* Update API Gateway url in scoreboard.html
* Upload the files to S3 for website hosting

## Final Testing
Ensure the following:
* `ddr_camera` is running on raspberry pi (right now it's written to run for 200 iterations)
* `sqs_poller` and `ddb_util_test` are running on openpose EC2 instance
* scoreboard.html on s3 website should display the updating scores.
  * e.g. http://ddr-s3-webapp.s3-website-us-west-2.amazonaws.com/