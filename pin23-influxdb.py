#import Libraries
import RPi.GPIO as GPIO
import os
import glob
import time
import urllib2
import statsd
import requests
from threading import Thread

url = 'http://localhost:8086/write?db=home'



# gpio pins for s0 kwhmeter
kwhmeters= {}
kwhmeters[0,0] = 'power1'
kwhmeters[0,1] = 23

oldcounter = 0
delta = 0
watt = 0
oldtime = 0
newtime = 0
#timer is in seconds
countertimer = 60

# Vermogen (in Watt) = Impulsen / Impulsconstante * 1000

# Dus watt = impulsecounter * 0,5 (1000/2000, waar 2000 aantal pulsen per kwh is)



def process_counter(name, pin):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	global counter
	counter = 0
	while True:
    		GPIO.wait_for_edge(pin, GPIO.RISING)
		counter += 1
    		GPIO.wait_for_edge(pin, GPIO.FALLING)
	GPIO.cleanup()

startreading = Thread(target=process_counter, args=(kwhmeters[0,0],kwhmeters[0,1],))
startreading.start()


processcounter = 0
while True:
        # print "Counter is now ", counter
        influxvalues = ""
        oldcounter = counter
        oldtime = newtime
        time.sleep(countertimer)
        newtime = round(time.time())
        timedelta = newtime - oldtime
        delta = counter - oldcounter
        wh = (delta*0.5)
        hourdelta = timedelta / 3600;
        watts = wh / hourdelta;
        if processcounter > 0:
	  print "Usage over last ", timedelta , " seconds: ", wh, "Wh or ", watts, "W"
	  influxvalues = influxvalues + 'power,sensor=heatpump value=' + str(watts)
	  print influxvalues
	  print url
	  requests.post(url,influxvalues)
	processcounter += 1
	print "DEBUG: counter:",counter,"oldcounter:",oldcounter,"newtime:",newtime,"timedelta:",timedelta,"hourdelta:",hourdelta
