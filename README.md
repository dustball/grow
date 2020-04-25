# Grow

![Sample output](https://raw.githubusercontent.com/dustball/grow/master/sample.jpeg)

Features:

* Monitor the enviroment
* Optionally control temperature with Wemo switches (edit the script to control other devices)
* Optionally report soil moisture on a per-plant basis (up to 8) 
* E-mail alerts when enviroment exceeds alarm values

Requires:

* [Ecowitt GW1000 WiFi gateway](https://www.amazon.com/gp/product/B07JLRFG24?tag=grow00c0-20) 
* [Linux](https://amzn.to/3cL3xMs), apache, MySQL, python3

Optional:

* [Wemo switches](https://www.amazon.com/gp/product/B0776YH29B?tag=grow00c0-20) for automation 
* [IP Webcam](https://www.amazon.com/gp/product/B0145OQTPG?tag=grow00c0-20) 
* Ecowitt [soil moisture sensors](https://www.amazon.com/gp/product/B07JM621R3?tag=grow00c0-20) 

See my [full grow list](list.md).

*As an Amazon Associate I earn from qualifying purchases.*

## Installation

1. Prepare linux host with working MySQL and python3.
2. Place files under the web root and make sure `.py` files execute as CGI
3. Create a database called `grow` and create tables with `mysql> create database grow` and `mysql grow < schema.mysql`.
4. `cp myconfig.sample myconfig.py` and edit cofiguration.  
5. Configure Ecowitt GW1000 to post data to `ecowitt.py` (Use "WS View" app, go to "Weather Services -> Customized", enter server address, `/ecowitt.py` as path, upload interval 60.
6. Copy `grow.service` to `/etc/systemd/system` and edit to make the `grow-control.py` run at boot, and restart on crash.  `systemctl daemon-reload` once in place, then `systemctl enable grow` then `service grow start` then `service grow status`.

Wemo automation:

1. Install [ouimeaux](https://github.com/iancmcc/ouimeaux)
2. Test command line: `wemo list`
3. Make sure device names match those in `grow-control.py`.

Webcam setup:

1. Edit `get-image.bash` to fetch an image from your webcam so the python script can add to it. 
2. Create a cronjob to run the above script every minute: `* * * * * /path/to/get-image.bash`
3. Run the script by hand to test it creates output as expected
4. Fetch `out.jpg` via your webserver 
5. Optionally speciy location (x,y coordinates with 0,0 at top left) of pots/soil sensors in config file
