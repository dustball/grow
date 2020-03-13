#!/bin/bash


wget "http://view:view1234@192.168.0.43:80/cgi-bin/snapshot.cgi" -O /var/www/html/image-dl.jpg

cp /var/www/html/image-dl.jpg /var/www/html/image.jpg
