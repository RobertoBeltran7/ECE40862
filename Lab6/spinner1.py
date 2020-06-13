from machine import TouchPad, Pin, RTC, Timer
import machine
from time import sleep
import ubinascii
import esp32
import math
import uos
from machine import I2C
import upip
import random
import urequests
import uhashlib
from ucryptolib import aes
try:
    from struct import unpack
except ImportError:
    from ustruct import unpack   
    
_ADXL345_MG2G_MULTIPLIER = 0.004 # 4mg per lsb
_STANDARD_GRAVITY = 9.80665 # earth standard gravity
client_id = ubinascii.hexlify(machine.unique_id())
mqtt_server = "farmer.cloudmqtt.com"
userid = 'gvbegkcy'
password="hlEKm7Uh5n_j"
port = 14209
sessionID = None
acknowledge = None
ifttt_url = "https://maker.ifttt.com/trigger/new_data/with/key/cKLoy7DqCWHW-elpHImdOb"

import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect('No Devices found', 'ssss1111')
    while not wlan.isconnected():
        pass
print("Oh Yes! Got connected")
#upip.install("micropython-hmac")
#upip.install("micropython-hashlib")
#upip.install("micropython-umqtt")
from crypt import CryptAes
from umqtt.simple import MQTTClient


def sub_cb(topic, msg):
    global sessionID, acknowledge
    if topic == b"SessionID":
        sessionID = msg
    elif topic == b"Acknowledge":
        acknowledge = msg
        sessionID = None

def connect_and_subscribe():
    global client_id, mqtt_server, userid, password, port
    client = MQTTClient(client_id,server=mqtt_server,
                        user=userid,password=password,port=port)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(b"SessionID")
    client.subscribe(b"Acknowledge")
    #print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()

def ifttt_upload_data(SessionID,ax,ay,az,temperature):
    sensor_data = "{0:06.3f} ||| {1:06.3f} ||| {2:06.3f}".format(ax,ay,az)
    temp = "{0:06.3f}".format(temperature)
    ifttt_data = {'value1': str(SessionID), 'value2': sensor_data, 'value3': temp}
    request_headers = {'Content-Type': 'application/json'}
    request = urequests.post(ifttt_url, json=ifttt_data, headers=request_headers)
    request.close()

try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()

sensor_data = "{} ||| {} ||| {}".format("ax","ay","az")
ifttt_data = {'value1':"SessionID", 'value2': sensor_data, 'value3': "temp"}
request_headers = {'Content-Type': 'application/json'}
request = urequests.post(ifttt_url, json=ifttt_data, headers=request_headers)
request.close()

button1 = machine.Pin(27, machine.Pin.IN)
button2 = machine.Pin(33,machine.Pin.IN)
switch1 = 0
switch2 = 0
oldtemp = 0
onLED = machine.Pin(13, machine.Pin.OUT)
timer_acc = machine.Timer(0)
flag = 0

# Initialization
i2c = I2C(sda= Pin(23),scl=Pin(22),freq=400000)          # create I2C peripheral at frequency of 400kHz
if len(i2c.scan()) != 2:
    raise ValueError("None or One of the sensors not detected")

if 83 not in i2c.scan() or 72 not in i2c.scan():
    raise ValueError("One or more sensors not accesible")

print("Initialization Complete")
def handleInterruptAcc(timer):
    global flag
    flag = flag+1
    
def handlerSwitch1(Pin):
    global switch1
    switch1 += 1
    
def handlerSwitch2(Pin):
    global switch2
    global switch1
    if switch1 >= 1:
        switch2 += 1
    

button1.irq(trigger = Pin.IRQ_FALLING,handler=handlerSwitch1)
button2.irq(trigger = Pin.IRQ_FALLING,handler=handlerSwitch2)
timer_acc.init(period=3000, mode=machine.Timer.PERIODIC, callback=handleInterruptAcc)

temp = 0

while True:
    if switch1 >= 1 and temp == 0:
        switch2 = 0
        temp = 1
        onLED.value(1)
        #Accelerometer configuration
        i2c.writeto_mem(83, 0x31, b'\x08') #Set Resolution
        i2c.writeto_mem(83, 0x2c, b'\x0d') #Set ODR
        i2c.writeto_mem(83, 0x2d, b'\x08') #Set ODR
        print("Initialized Accelerometer")
        i2c.writeto_mem(83, 0x1E, bytes([0])) #Set ODR
        i2c.writeto_mem(83, 0x1F, bytes([0])) #Set ODR
        i2c.writeto_mem(83, 0x20, bytes([0])) #Set ODR
        print("Calibrated Accelerometer")
        #   Temperature Calibrations
        i2c.writeto_mem(72, 0x03, b'\x80') #Set ODR
        print("Initialized Temperature Sensor\n")
        lsbt =i2c.readfrom_mem(72,0x01, 1)
        msbt =i2c.readfrom_mem(72,0x00, 1)
        value = (msbt[0] << 8) | lsbt[0]
        oldtemp = (value & 0x7fff)/128
        if value & 0x1000:
            oldtemp -= 256.0
    
    if switch2 >= 1:
        switch1 = 0
        temp = 0
        onLED.off()
        client.check_msg()
        if sessionID is not None:
            flag = 0
            x,y,z =0,0,0
            for i in range(50):
                data = i2c.readfrom_mem(83,0x32, 6)
                xtemp,ytemp,ztemp = unpack('<hhh', data)
                x += xtemp
                y += ytemp
                z += ztemp
            x /= 50
            y /= 50
            z /= 50
            
            # Calculate acceleration
            ax = (x * _ADXL345_MG2G_MULTIPLIER -0.004) * _STANDARD_GRAVITY
            ay = y * _ADXL345_MG2G_MULTIPLIER * _STANDARD_GRAVITY
            az = (z * _ADXL345_MG2G_MULTIPLIER +0.005)* _STANDARD_GRAVITY
            a = math.sqrt(ax*ax+ay*ay+az*az)

            data = {}
            data["ax"] = ax
            data["ay"] = ay
            data["az"] = az               
            '''
                Measure Temperature
            '''
            lsb =i2c.readfrom_mem(72,0x01, 1)
            msb =i2c.readfrom_mem(72,0x00, 1)
            value = (msb[0] << 8) | lsb[0]
            newtemp = (value & 0x7fff)/128
            if value & 0x1000:
                newtemp -= 256.0
            #print("Temperature: {}\n".format(newtemp))
            data["temp"] = newtemp 
            encryption = CryptAes(sessionID)
            encryption.encrypt(data)
            hmac_sign = encryption.sign_hmac(sessionID)
            publish_msg = encryption.send_mqtt(hmac_sign)
            #print(publish_msg)
            client.publish(b"Sensor_Data", publish_msg)
            if flag > 0:
                ifttt_upload_data(sessionID,ax,ay,az,newtemp)
                flag = 0
            #client.subscribe(b"Acknowledge")
            while True:
                client.check_msg()
                if acknowledge is not None:
                    print(acknowledge)
                    acknowledge = None
                    break;
