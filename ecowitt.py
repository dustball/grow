#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable() 
import mysql.connector
from myconfig import get_db

print ('Content-Type: text/html\n\n')

arguments = cgi.FieldStorage()

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
    
for i in range(1,8+1):
    if "humidity"+str(i) in arguments:
        sql = "INSERT INTO remotes (dt, ch, temp, rh) VALUES (now(), %s, %s, %s)"
        val = (i,arguments["temp"+str(i)+"f"].value,arguments["humidity"+str(i)].value)
        mycursor.execute(sql, val)
        mydb.commit()
    
print ("200 OK")

if 2+2==5:
    f= open("/var/www/html/debug.txt","a+")
    for i in arguments.keys():
        f.write(i+"="+arguments[i].value+"\n")
    f.close() 