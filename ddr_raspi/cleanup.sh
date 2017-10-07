#! /bin/bash
#Clean up old image files
find ~/images -mmin +15 -type f -name "*.jpg" -exec rm -f {} \;