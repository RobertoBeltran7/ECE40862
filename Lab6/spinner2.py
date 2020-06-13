import machine
from machine import Pin, Timer,PWM
import crypt
import network
import upip
from umqtt.simple import MQTTClient
import umqtt.robust
import hmac
import ubinascii
import uos
import utime
import esp32
from hashlib import sha224
import hashlib
import math
import socket
import urequests
import json

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
        
connect_wifi()
utime.sleep(1)
#upip.install("micropython-umqtt.simple")
#upip.install("micropython-umqtt.robust")
#upip.install("micropython-hmac")

SessionID=0
client_ID = "ESP32 Device"
server= "farmer.cloudmqtt.com"
topic1=b"SessionID"
topic2=b"Sensor_Data"
topic3=b"Acknowledge"

A_X=9
A_Y=9
A_Z=9

red_led = Pin(21,Pin.OUT)
green_led_pwm = PWM(Pin(14),freq=10,duty=512)
board_led = Pin(13,Pin.OUT)
red_led.off()
board_led.off()

def generate_randomID():
    global SessionID
    SessionID = uos.urandom(16)
    global topic1
    client.publish(topic1,SessionID)

waiting_msg=1
sensor_hmacdata=0
prev_temp=0

def sub_cb(topic,msg):
    global waiting_msg
    waiting_msg=0
    global sensor_hmacdata
    sensor_hmacdata=msg


#Create MQTT Client
client = MQTTClient(client_ID,server,port=14209,user='gvbegkcy',password='hlEKm7Uh5n_j')
client.set_callback(sub_cb)
client.connect()


def ifttt_upload_data(a_x,a_y,a_z,temperature):
    sensor_data = "{0:06.3f} ||| {1:06.3f} ||| {2:06.3f}".format(a_x,a_y,a_z)
    temp = "{0:06.3f}".format(temperature)
    ifttt_data = {'value1': str(SessionID), 'value2': sensor_data, 'value3': temp}
    request_headers = {'Content-Type': 'application/json'}
    request = urequests.post('http://maker.ifttt.com/trigger/sensor_data/with/key/dHIbgWcG3E7_2y-aC72K1P', json=ifttt_data, headers=request_headers)
    request.close()
a_x=0
a_y=0
a_z=0
temp=0
tim2=Timer(2)
tim2.init(period=3000,mode=Timer.PERIODIC,callback=lambda t:ifttt_upload_data(a_x,a_y,a_z,temp))
    
client.subscribe(topic2)

while True:
    SessionID = uos.urandom(16)
    client.publish(topic1,SessionID)
    while waiting_msg:
        client.check_msg()
    
    waiting_msg=1
    
    crypt_data = crypt.CryptAes(SessionID)
    verifying_hmac = crypt_data.verify_hmac(sensor_hmacdata)
    
    if verifying_hmac != b'HMAC Authenticated':
        client.publish(topic3,verifying_hmac)
    else:
        decrypt_msg, decrypted_data = crypt_data.decrypt(sensor_hmacdata)
        a_x=decrypted_data['a_x']
        a_y=decrypted_data['a_y']
        a_z=decrypted_data['a_z']
        temp=decrypted_data['temp']
        client.publish(topic3,b'Successful Decryption')
        utime.sleep_ms(100)
        if (a_x > A_X) or (a_y > A_Y) or (a_z > A_Z):
            red_led.on()
        else:
            red_led.off()
            
        if (prev_temp == 0):
            prev_temp=temp
        else:
            diff = temp - prev_temp
            if math.fabs(diff) >= 1:
                green_led_pwm.freq(green_led_pwm.freq()+diff)
                prev_temp = temp
     
    utime.sleep_ms(100)



