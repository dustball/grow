#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable() 
import mysql.connector
from myconfig import get_db
import os
import time


print ('Content-Type: text/html\n')

arguments = cgi.FieldStorage()

mydb = get_db()
mycursor = mydb.cursor()
mycursor.execute("select id,TIMESTAMPDIFF(SECOND,dt,now()) as old,temp,rh from eco order by id desc limit 1")

for (id, old, temp, rh) in mycursor:
    if (old>300):
        print ("Error: temp too old")
    else:
        st = os.stat("out.jpg")
        mtime = time.time() - st.st_mtime
        if (mtime>300):
            print ("Error: out.jpg too old")
        else:
            print ("OK")
