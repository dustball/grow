#!/bin/bash

set -e

wget "http://view:view1234@192.168.0.43:80/cgi-bin/snapshot.cgi" -O image-dl.jpg

cp image-dl.jpg image.jpg
