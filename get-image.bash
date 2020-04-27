#!/bin/bash

pkill -9 wget

set -e

wget --timeout 8 -r --tries=5 -w 2 --retry-connrefused "http://view:view1234@192.168.0.43:80/cgi-bin/snapshot.cgi" -O image-dl.jpg

cp image-dl.jpg image.jpg
