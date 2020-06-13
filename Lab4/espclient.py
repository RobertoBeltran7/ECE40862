from machine import Pin
from machine import Timer
from machine import RTC
from ntptime import time
import machine
import dht
import esp32
import usocket
import socket
import ssl
import network
import ubinascii

def turn_to_MAC(data):
    return ':'.join('%02x' % b for b in data)

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect('MSI 6365','172K%2f8')
    if wifi.isconnected():
        print('Oh Yes! Get connected')
        print('Connected to', wifi.config('essid'))
        mac_address = turn_to_MAC(wifi.config('mac'))
        print('MAC Address:', mac_address)
        print('IP Address:', wifi.ifconfig()[0])

def fullSend(counter):
  temperature = str(esp32.raw_temperature())
  hall_sensor = str(esp32.hall_sensor())
  print("Temperature is " + temperature)
  print("Hall is " + hall_sensor)

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  address = socket.getaddrinfo('api.thingspeak.com', 80)[0][-1]
  s.connect(address)
  s.send("GET http://api.thingspeak.com/update?api_key=3VDFM8XC3RT41CEJ&field1="+temperature+"&field2="+hall_sensor+"HTTP/1.0\r\n\r\n")
  counter += 1
  print(s.recv(1024))
  s.close()
  
  
if __name__ == "__main__":
  connect_wifi()
  counter = 0
  hardTimer = Timer(1)
  hardTimer.init(mode=Timer.PERIODIC, period=17000, callback=lambda t:fullSend(counter))
  print("Server Communicated")