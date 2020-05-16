#!/usr/bin/python3

from datetime import datetime
from myconfig import get_db, get_mgkey, get_domain, get_email, get_pots
import mysql.connector
import subprocess
import time
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import sys
import os
import requests

retries = 5

mydb = get_db()
        
def main():        
    alarmed_sigma = 0
    rh_alarmed_sigma = 0
    
    send_start()
    
    while True:
        
        extra = ""
        
        print ("")
        print (str(datetime.now())[:-4])
        now = datetime.now()
        hour = now.hour
            
        high_temp = 76
        low_temp = 72
        alarm_rh_low = 40
        alarm_rh_high = 55
        alarm_delay_minutes = 10
            
        if (hour>=2 and hour<8):
            high_temp = high_temp - 8
            low_temp = low_temp - 8
            
        if (hour==2 or hour==8):
             alarm_delay_minutes = 55
                 
        alarm_temp_low = low_temp - 3
        alarm_temp_high = high_temp + 3

        if (hour>=2 and hour<8):
            alarm_temp_high = alarm_temp_high + 5
 
        heater1 = get_status("1")    
        heater2 = get_status("2")    
        lights = get_lightstatus()
        
        mycursor = mydb.cursor()
        mycursor.execute("select id,TIMESTAMPDIFF(SECOND,dt,now()) as old,temp,rh from eco order by id desc limit 1")
        
        sleep = 60
            
        for (id, old, temp, rh) in mycursor:
            if (old<55):
                sleep = 60 - old
            if (old<200):
                print ("Temperature = ", end='')
                print (temp)
                            
                if (temp>1 and temp<alarm_temp_low):
                    print ("*Alarm State Low*")
                    extra = extra + "\n*Temp Low*\n"
                    alarmed_sigma = alarmed_sigma + 1
                    if (alarmed_sigma==alarm_delay_minutes):
                        send_alarm(temp)                    
                elif (temp>alarm_temp_high):
                    print ("*Alarm State High*")
                    extra = extra + "\n*Temp High*\n"
                    alarmed_sigma = alarmed_sigma + 1
                    if (alarmed_sigma==alarm_delay_minutes):
                        send_alarm(temp)                    
                else:
                    alarmed_sigma = 0
                    
                if (rh>1 and temp<alarm_rh_low):
                    print ("*RH Alarm State Low*")
                    extra = extra + "\n*RH Low*\n"                    
                    rh_alarmed_sigma = rh_alarmed_sigma + 1
                    if (rh_alarmed_sigma==alarm_delay_minutes):
                        send_rh_alarm(rh)                    
                elif (rh>alarm_rh_high):
                    print ("*RH Alarm State High*")
                    extra = extra + "\n*RH High*\n"                    
                    rh_alarmed_sigma = rh_alarmed_sigma + 1
                    if (rh_alarmed_sigma==alarm_delay_minutes):
                        send_rh_alarm(rh)                    
                else:
                    rh_alarmed_sigma = 0
                
                # If it is really cold, turn both heaters on
                if (temp<low_temp):
                    if (heater1=="off"):
                        turn_on(temp,"1")
                        extra = extra + "Turn on 1\n"                        
                    if (heater2=="off"):
                        turn_on(temp,"2")
                        extra = extra + "Turn on 2\n"                        
                
                # If it is really hot, turn both heaters off        
                if (temp>high_temp):
                    if (heater1=="on"):
                        turn_off(temp,"1")
                        extra = extra + "Turn off 1\n"                        
                    if (heater2=="on"):
                        turn_off(temp,"2")
                        extra = extra + "Turn off 2\n"                        
    
                # If it is in between, just change one of the heaters 
                if (temp>=low_temp and temp<=high_temp):
                    if (temp < low_temp+1 and heater1=="off"):
                        turn_on(temp,"1")
                        extra = extra + "Turn on 1\n"                                                
                    if (temp > high_temp-1 and heater1=="on"):
                        turn_off(temp,"1")
                        extra = extra + "Turn off 1\n"                                                
            else:
                print ("Temperature too old (",old,")\n", end='')
                extra = extra + "Sensor OOD\n"                                                
        
        make_image(temp,rh,heater1,heater2,lights,alarmed_sigma,rh_alarmed_sigma,extra)
                                    
        print ("Sleep = ", sleep, "\n", end='')
        print ("")
        time.sleep(sleep)       
        

def make_image(temp,rh,heater1,heater2,lights,alarmed_sigma,rh_alarmed_sigma,extra):               
    try:
        text = str(temp)+"°F\n"+str(round(rh))+"% RH\n\n"+"Heater 1: "+heater1+"\n"+"Heater 2: "+heater2+"\n"+"Lights: "+lights+"\n"
        if alarmed_sigma>0:
            text = text + "Alarm Min: "+str(alarmed_sigma)+"\n"
        if rh_alarmed_sigma>0:
            text = text + "Alarm Min: "+str(rh_alarmed_sigma)+"\n"
        if extra:
            text = text + "\n" + extra
        img = Image.open("image.jpg")
        drop = Image.open("waterdrop.png") 
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
        x = 1630
        y = 20
        draw.text((x-2, y), text, (0, 0, 0), font=font, align="right")
        draw.text((x+2, y), text, (0, 0, 0), font=font, align="right")
        draw.text((x, y-2), text, (0, 0, 0), font=font, align="right")
        draw.text((x, y+2), text, (0, 0, 0), font=font, align="right")
        draw.text((x-2, y-2), text, (0, 0, 0), font=font, align="right")
        draw.text((x+2, y-2), text, (0, 0, 0), font=font, align="right")
        draw.text((x-2, y-2), text, (0, 0, 0), font=font, align="right")
        draw.text((x+2, y+2), text, (0, 0, 0), font=font, align="right")
        draw.text((x, y), text, (255, 255, 255), font=font, align="right")
    
        pots = get_pots()
        mycursor = mydb.cursor()
         
    
        for i in range(1,len(pots)+1):
            sql = "select percent, batt from soil where ch="+str(i)+" order by dt desc limit 1"
            mycursor.execute(sql)
            for (percent,batt) in mycursor:
                xy = pots[i-1]
                x = xy[0]
                y = xy[1]
                width = 100
                height = 30
                if x != 0:
                    draw.rectangle((x, y, x+width, y+height), fill=(0, 0, 0), outline=(255, 255, 255))
                    inside = (0, 200, 0)
                    if (percent < 20):
                        inside = (200,200,40)
                    if (percent<10):
                        inside = (250,0,0)
                    draw.rectangle((x+1, y+1, x+ ((width-1)*percent/100), y+height-1), fill=inside)
                    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
                    text = "Ch"+str(i)+" "+str(percent)+"%"
                    y = y + 36
                    draw.text((x-2, y), text, (0, 0, 0), font=font, align="right")
                    draw.text((x+2, y), text, (0, 0, 0), font=font, align="right")
                    draw.text((x, y-2), text, (0, 0, 0), font=font, align="right")
                    draw.text((x, y+2), text, (0, 0, 0), font=font, align="right")
                    draw.text((x, y), text, (255, 255, 255), font=font, align="right")
                    
                    img.paste(drop, (x-25, y-35 ), drop) 

        img.save("out.jpg")
    except Exception as e:
        print ("Error with image process = ",e)           



def turn_on(temp,x):
    print ("Turning On "+x)
    i = 0
    while True:
        i = i + 1
        result = subprocess.run(['wemo', 'switch', 'Heater '+x, 'on'], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8').rstrip()
        if (output==""):
            mycursor = mydb.cursor()
            sql = "INSERT INTO heaters (dt, temp, heater, state) VALUES (now(), %s, %s, %s)"
            val = (temp, x, "on")
            mycursor.execute(sql, val)
            mydb.commit()            
        if (i>retries or output==""):
            break
        print ("Retry turn_on "+x+"...")

def turn_off(temp,x):
    print ("Turning Off "+x)
    i = 0
    while True:
        i = i + 1
        result = subprocess.run(['wemo', 'switch', 'Heater '+x, 'off'], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8').rstrip()
        if (output==""):
            mycursor = mydb.cursor()
            sql = "INSERT INTO heaters (dt, temp, heater, state) VALUES (now(), %s, %s, %s)"
            val = (temp, x, "off")
            mycursor.execute(sql, val)
            mydb.commit()            
        if (i>retries or output==""):
            break
        print ("Retry turn_off "+x+"...")

def get_status(x):
    i = 0
    while True:
        i = i + 1
        result = subprocess.run(['wemo', '-v', 'switch', 'Heater '+x, 'status'], stdout=subprocess.PIPE)        
        output = result.stdout.decode('utf-8').rstrip()
        if (i>retries or output=="on" or output=="off"):
            break
        print ("Retry get_status "+x+"...")
    if output == "No device found with that name.":
        output = "err"
    print ("Heater "+x+" status = ", end='')
    print (output)
    return output    

def get_lightstatus():
    i = 0
    while True:
        i = i + 1
        result = subprocess.run(['wemo', '-v', 'switch', 'Grow lights', 'status'], stdout=subprocess.PIPE)        
        output = result.stdout.decode('utf-8').rstrip()
        if (i>retries or output=="on" or output=="off"):
            break
        print ("Retry get_lightstatus ...")
    if output == "No device found with that name.":
        output = "err"
    print ("Light status = ", end='')
    print (output)
    return output                

def send_start():
    now = datetime.now()
    dt_string = now.strftime("%m/%d %H:%M")
    return requests.post(
        "https://api.mailgun.net/v3/mg."+get_domain()+"/messages",
        auth=("api", get_mgkey()),
        data={"from": "Grow Room <grow@mg."+get_domain()+">",
              "to": [get_email()],
              "subject": "Start - "+dt_string,
              "text": "<end of msg>"})
              
def send_alarm(temp):
    return requests.post(
        "https://api.mailgun.net/v3/mg."+get_domain()+"/messages",
        auth=("api", get_mgkey()),
        data={"from": "Grow Room <grow@mg."+get_domain()+">",
              "to": [get_email()],
              "subject": "Temperature Alert - "+str(temp)+"°F",
              "text": "<end of alert>"})

def send_rh_alarm(rh):
    return requests.post(
        "https://api.mailgun.net/v3/mg."+get_domain()+"/messages",
        auth=("api", get_mgkey()),
        data={"from": "Grow Room <grow@mg."+get_domain()+">",
              "to": [get_email()],
              "subject": "Humidity Alert - "+str(rh)+"%",
              "text": "<end of alert>"})

if __name__== "__main__":
    main()
    