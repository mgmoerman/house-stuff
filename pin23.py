#import Libraries
import RPi.GPIO as GPIO
import os
import glob
import time
import urllib2
from threading import Thread

# emoncms params
write_api = 'ce8852c1404a68d79b38a8cf018b09c5'
url = 'http://172.26.0.164/emoncms/input/post.json'

# gpio pins for s0 kwhmeter
kwhmeters= {}
kwhmeters[0,0] = 'power1'
kwhmeters[0,1] = 23


def process_counter(name, pin):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

	counter = 0
	while True:
    		GPIO.wait_for_edge(pin, GPIO.RISING)
		counter += 1
    		print "Counter is now ", counter, " watt = ", counter/2000.0, "kWh"
    		GPIO.wait_for_edge(pin, GPIO.FALLING)
    		json_url = url + "?node=1&json={"+name+":"+str(counter)+"}&apikey="+write_api
		influxjson = "[{\"name:power\",\"columns\":[\"" + name +"\"],\"points\":[[pulse]]}]"
		print (influxjson)
    		print (json_url)
    		urllib2.urlopen(json_url).read()

	GPIO.cleanup()

startreading = Thread(target=process_counter, args=(kwhmeters[0,0],kwhmeters[0,1],))
startreading.start()
