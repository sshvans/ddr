#!/bin/bash
# Author: Shivansh Singh
# This script outlines the steps to install and configure openpose library on
# Ubuntu 16.04, P2 instance type on AWS

sudo apt-get update -y
sudo apt-get -y install python-setuptools
sudo easy_install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz

###### Install NVDIA driver ######
# Ref: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/accelerated-computing-instances.html

sudo apt-get update -y
# Install make
sudo apt-get install build-essential -y
# Upgrade the linux-aws package to receive the latest version
sudo apt-get upgrade -y linux-aws
# Reboot your instance to load the latest kernel version
sudo reboot
# Install the gcc compiler and the kernel headers package for the version of
# the kernel you are currently running.
sudo apt-get install -y gcc linux-headers-$(uname -r)
# Download the driver package that you identified earlier. For P2 instances,
# the following command downloads the 375.66 version of the NVIDIA driver
wget http://us.download.nvidia.com/XFree86/Linux-x86_64/375.66/NVIDIA-Linux-x86_64-375.66.run
# Run the self-install script to install the NVIDIA driver that you downloaded
sudo /bin/bash ./NVIDIA-Linux-x86_64-375.66.run
# On-prompt, Accept the license agreement and ignore the warnings
# Reboot instance
sudo reboot
# Confirm that the driver is functional by running following command.
# It make take several minutes
nvidia-smi -q | head


###### Install CUDA ######

# Download CUDA package from an s3 bucket.
wget https://s3-us-west-2.amazonaws.com/lib-ddr/templates/cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
# Unpack and install
sudo dpkg -i cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
sudo apt-get update -y
sudo apt-get install cuda -y
# Must reboot the system after installing CUDA
# This installs CUDA 8.0 at /usr/local/cuda-8.0
sudo reboot


###### Install cuDNN ######

# Download cuDNN package from an s3 bucket.
wget https://s3-us-west-2.amazonaws.com/lib-ddr/templates/cudnn-8.0-linux-x64-v5.1.tgz
# unzip it and copy (merge) the contents on the CUDA folder i.e. /usr/local/cuda-8.0
cd /usr/local/
sudo tar -xvzf ~/cudnn-8.0-linux-x64-v5.1.tgz


###### Install OpenCV ######

sudo apt-get update -y
sudo apt-get install libopencv-dev -y
sudo apt-get install libatlas-base-dev -y

###### Install openpose ######
cd ~
git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose.git
cd openpose
sudo apt-get install python-pip -y
sudo apt-get install python-numpy -y
chmod 755 ./ubuntu/install_caffe_and_openpose_if_cuda8.sh
sudo ./ubuntu/install_caffe_and_openpose_if_cuda8.sh
