#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable() 
import mysql.connector
from myconfig import get_db

print ('Content-Type: text/html\n\n')

arguments = cgi.FieldStorage()

if 2+2==5:
    f= open("out.txt","a+")
    for i in arguments.keys():
        f.write(i+"="+arguments[i].value+"\n")
    f.close() 

if "tempinf" in arguments and "humidityin" in arguments:
    mydb = get_db()
    mycursor = mydb.cursor()
    sql = "INSERT INTO eco (dt, temp, rh) VALUES (now(), %s, %s)"
    val = (arguments['tempinf'].value,arguments['humidityin'].value)
    mycursor.execute(sql, val)
    mydb.commit()

for i in range(1,8+1):
    if "soilmoisture"+str(i) in arguments:
        sql = "INSERT INTO soil (dt, ch, percent, batt) VALUES (now(), %s, %s, %s)"
        val = (i,arguments["soilmoisture"+str(i)].value,arguments["soilbatt"+str(i)].value)
        mycursor.execute(sql, val)
        mydb.commit()
    
print ("200 OK")

#soilbatt2=1.7
#dateutc=2020-03-09 15:50:49
#baromabsin=29.137
#soilmoisture6=27
#tempinf=76.6
#soilbatt5=1.8
#soilmoisture4=30
#soilbatt3=1.8
#model=GW1000_Pro
#soilmoisture5=36
#soilmoisture1=40
#freq=915M
#stationtype=GW1000B_V1.5.6
#soilmoisture2=25
#soilbatt6=1.7
#baromrelin=29.137
#PASSKEY=xxxx
#soilbatt1=1.7
#soilmoisture3=26
#soilbatt4=1.8
#humidityin=62