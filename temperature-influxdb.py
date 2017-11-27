#import libs
import os
import glob
import time
import requests


url_elburg = 'http://home.kpn.nl/E.rozenberg/index.htm'
# temp sensors

base_dir = '/sys/bus/w1/devices/'
temperature_content = '/w1_slave'
sensors_w, sensors_h = 8, 2;
sensors = {}

sensors[0,0] = 'slaapkamer2'
sensors[0,1] = '28-0316855ecbff'
sensors[1,0] = 'slaapkamer1'
sensors[1,1] = '28-041685e8c3ff'

sensors[2,0] = 'boven1'
sensors[2,1] = '28-03168116e9ff'
sensors[3,0] = 'badkamer1'
sensors[3,1] = '28-03168117b0ff'
sensors[4,0] = 'boven3'
sensors[4,1] = '28-03168117d6ff'
sensors[5,0] = 'boven4'
sensors[5,1] = '28-0316855da2ff'
sensors[6,0] = 'boven5'
sensors[6,1] = '28-0516819621ff'
sensors[7,0] = 'badkamer2'
sensors[7,1] = '28-051686bbbcff'






#sensors[2,0] = 'souterrain1'
#sensors[2,1] = '28-03168114fdff'
#sensors[3,0] = 'souterrain2'
#sensors[3,1] = '28-0416816e78ff'
#sensors[4,0] = 'souterrain3'
#sensors[4,1] = '28-0516811d57ff'
#sensors[5,0] = 'souterrain4'
#sensors[5,1] = '28-0516868ac6ff'


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


def get_elburg_temp():
  r = requests.get(url_elburg, stream=True)
  z = 0
  for line in r.iter_lines():
    z = z + 1
    if line:
      if z == 112:
        return str(float(filter(str.isdigit, line))/10)
    
# populate and assemble URL
timer = 0
while True:
  sensor_values = ""
  if timer >= 9: timer = 0
  timer = timer + 1
  for x in range(0,sensors_w): 
        if x > 0:
          if x < sensors_w: sensor_values = sensor_values + '\n' 
	sensor_values = sensor_values + 'temperature,sensor='+ sensors[x,0] + ' value=' + str(parse_temp(sensors[x,1])) 
	if sensors[x,0] == 'slaapkamer2':
	  Ta = str(parse_temp(sensors[x,1]))
        if sensors[x,0] == 'slaapkamer1':
          Tr = str(parse_temp(sensors[x,1]))
  # sensor_values = urllib.quote('{' + sensor_values + '}')
  Td = float(Ta) - float(Tr)
  print (url)
  print "Delta = ", Td  
  
  sensor_values = sensor_values + '\ntemperature,sensor=DeltaT' + ' value=' + str(Td)
  if timer == 1: sensor_values = sensor_values + '\ntemperature,sensor=buiten value=' + str(get_elburg_temp())
  print (sensor_values)
  requests.post(url,sensor_values)
  time.sleep(60)
