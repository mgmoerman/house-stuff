#import libs
import os
import glob
import time
import requests

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
write_api = 'ce8852c1404a68d79b38a8cf018b09c5'
url = 'http://localhost:8086/write?db=home'


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

# populate and assemble URL
while True:
  sensor_values = ""
  for x in range(0,sensors_w):
        if x > 0:
          if x < 2: sensor_values = sensor_values + '\n'
	sensor_values = sensor_values + 'temperature,sensor='+ sensors[x,0] + ' value=' + str(parse_temp(sensors[x,1]))

  # sensor_values = urllib.quote('{' + sensor_values + '}')
  print (url)
  print (sensor_values)
  requests.post(url,sensor_values)
  time.sleep(60)
