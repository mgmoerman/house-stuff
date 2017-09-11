#import libs
import os
import glob
import time
import urllib2

# temp sensors

base_dir = '/sys/bus/w1/devices/'
temperature_content = '/w1_slave'
sensors_w, sensors_h = 2, 2;
sensors = {}

sensors[0,0] = 'slaapkamer1'
sensors[0,1] = '28-0316855ecbff'
sensors[1,0] = 'slaapkamer2'
sensors[1,1] = '28-041685e8c3ff'

# emoncms
write_api = 'XXXXX'
url = 'http://a.b.c.d/emoncms/input/post.json'


# Initialize the GPIO Pins
os.system('modprobe w1-gpio')  # Turns on the GPIO module
os.system('modprobe w1-therm') # Turns on the Temperature module


####################################################################################

#  read data
def read_temp_raw(sensor):
  f = open(base_dir+sensor+temperature_content, 'r') # Opens the temperature device file
  lines = f.readlines() # Returns the text
  f.close()
  return lines

#  convert sensor value to temperature
def parse_temp(sensor):
  lines = read_temp_raw(sensor) # Read the temperature 'device file'

  # While the first line does not contain 'YES', wait for 0.2s
  # and then read the device file again.
  while lines[0].strip()[-3:] != 'YES':
    time.sleep(0.2)
    lines = read_temp_raw()

  # Look for the position of the '=' in the second line of the
  # device file.
  equals_pos = lines[1].find('t=')

  # If the '=' is found, convert the rest of the line after the
  # '=' into degrees Celsius, then degrees Fahrenheit
  if equals_pos != -1:
    temp_string = lines[1][equals_pos+2:]
    temp_c = float(temp_string) / 1000.0
  #  temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_c

# populate JSON and assemble URL
while True:
  json_url = url + "?node=1&json={"
  sensor_values = ""
  for x in range(0,sensors_w):
        if x > 0:
          if x < 2: sensor_values = sensor_values + ","
	sensor_values = sensor_values + sensors[x,0]+":"+str(parse_temp(sensors[x,1]))
  json_url = json_url + sensor_values + "}&apikey=" + write_api

  print (json_url)
  urllib2.urlopen(json_url).read()
  time.sleep(60)
