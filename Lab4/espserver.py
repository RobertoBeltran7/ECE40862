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

def web_page(t, hal, rstate, gstate):
    temp = t
    hall = hal
    red_led_state = rstate
    green_led_state = gstate
    """Function to build the HTML webpage which should be displayed
    in client (web browser on PC or phone) when the client sends a request
    the ESP32 server.
    
    The server should send necessary header information to the client
    (YOU HAVE TO FIND OUT WHAT HEADER YOUR SERVER NEEDS TO SEND)
    and then only send the HTML webpage to the client.
    
    Global variables:
    TEMP, HALL, RED_LED_STATE, GREEN_LED_STAT
    """
    
    html_webpage = """<!DOCTYPE HTML><html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
    <style>
    html {
     font-family: Arial;
     display: inline-block;
     margin: 0px auto;
     text-align: center;
    }
    h2 { font-size: 3.0rem; }
    p { font-size: 3.0rem; }
    .units { font-size: 1.5rem; }
    .sensor-labels{
      font-size: 1.5rem;
      vertical-align:middle;
      padding-bottom: 15px;
    }
    .button {
        display: inline-block; background-color: #e7bd3b; border: none; 
        border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none;
        font-size: 30px; margin: 2px; cursor: pointer;
    }
    .button2 {
        background-color: #4286f4;
    }
    </style>
    </head>
    <body>
    <h2>ESP32 WEB Server</h2>
    <p>
    <i class="fas fa-thermometer-half" style="color:#059e8a;"></i> 
    <span class="sensor-labels">Temperature</span> 
    <span>"""+str(temp)+"""</span>
    <sup class="units">&deg;F</sup>
    </p>
    <p>
    <i class="fas fa-bolt" style="color:#00add6;"></i>
    <span class="sensor-labels">Hall</span>
    <span>"""+str(hall)+"""</span>
    <sup class="units">V</sup>
    </p>
    <p>
    RED LED Current State: <strong>""" + red_led_state + """</strong>
    </p>
    <p>
    <a href="/?red_led=on"><button class="button">RED ON</button></a>
    </p>
    <p><a href="/?red_led=off"><button class="button button2">RED OFF</button></a>
    </p>
    <p>
    GREEN LED Current State: <strong>""" + green_led_state + """</strong>
    </p>
    <p>
    <a href="/?green_led=on"><button class="button">GREEN ON</button></a>
    </p>
    <p><a href="/?green_led=off"><button class="button button2">GREEN OFF</button></a>
    </p>
    </body>
    </html>"""
    return html_webpage

    
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
    
if __name__ == "__main__":
    connect_wifi()
    
    p12 = Pin(12, Pin.OUT)
    p25 = Pin(25, Pin.OUT)
    if p12.value() == 0:
        RED_LED_STATE = "OFF"
    else:
        RED_LED_STATE = "ON"
    if p25.value() == 0:
        GREEN_LED_STATE = "OFF"
    else:
        GREEN_LED_STATE = "ON"
    temperature = str(esp32.raw_temperature())
    hall_sensor = str(esp32.hall_sensor())
    htmlwebpage = web_page(temperature, hall_sensor, RED_LED_STATE, GREEN_LED_STATE)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    while(True):
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        request = str(request)
        print('Content = %s' % request)
        redled_on = request.find('/?red_led=on')
        redled_off = request.find('/?red_led=off')
        greenled_on = request.find('/?green_led=on')
        greenled_off = request.find('/?green_led=off')
        if redled_on == 6:
          print('RED LED ON')
          p12.value(1)
          RED_LED_STATE = "ON"
        if redled_off == 6:
          print('RED LED OFF')
          p12.value(0)
          RED_LED_STATE = "OFF"
          
        if greenled_on == 6:
          print('GREEN LED ON')
          p25.value(1)
          GREEN_LED_STATE = "ON"
        if greenled_off == 6:
          print('GREEN LED OFF')
          p25.value(0)
          GREEN_LED_STATE = "OFF"
        temperature = esp32.raw_temperature()
        hall = esp32.hall_sensor()  
        response = web_page(temperature, hall, RED_LED_STATE, GREEN_LED_STATE)
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
    
    
    
    