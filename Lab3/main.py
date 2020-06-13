from machine import Pin, TouchPad
import network
from machine import RTC,Timer,TouchPad,Pin
from ntptime import settime
import ntptime
import utime
import machine
import esp32

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
if machine.wake_reason() == 4:
    print('Timer wake-up')
    
green_led = Pin(14,Pin.OUT)
green_led.on()
pushbutton1 = Pin(36,Pin.IN,Pin.PULL_DOWN)
pushbutton2 = Pin(4,Pin.IN,Pin.PULL_DOWN)
red_led = Pin(21,Pin.OUT)
red_led.on()
touch = TouchPad(Pin(15))
touch2 = TouchPad(Pin(32))
touch.config(400)
touch2.config(500)
esp32.wake_on_touch(True)

tm = ntptime.time()
tim = utime.localtime(tm-4*3600)
rtc = RTC()
rtc.datetime(tim[0:3]+ tim[6:7] + tim[3:6] + (0,))

def pDate(datetime):
    print('Date: '+ "{:02d}".format(datetime[1]) + '/' + "{:02d}".format(datetime[2]) + '/' + "{:02d}".format(datetime[0]))
    print('Time: ' + "{:02d}".format(datetime[4]) + ':' + "{:02d}".format(datetime[5]) + ':' + "{:02d}".format(datetime[6]) + ' '  + 'HRS')

timer = Timer(1)
timer.init(period=15000,mode=Timer.PERIODIC,callback=lambda t:pDate(rtc.datetime()))

def turn_on_green():
    #print('touch1:',touch.read())
    #print('touch2:',touch2.read())
    if touch.read() < 400:
        green_led.off()
    else:
        green_led.on()

timer2 = Timer(2)
timer2.init(period=10,mode=Timer.PERIODIC,callback=lambda t:turn_on_green())

def esp32_sleep():
    print('I am awake. Going to sleep for 1 minute')
    red_led.off()
    machine.deepsleep(60000)

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    red_led.on()

esp32.wake_on_ext1(pins=(pushbutton1,pushbutton2),level=esp32.WAKEUP_ANY_HIGH)
if machine.wake_reason() == 5:
    print('Touchpad wake-up')
    
if machine.wake_reason() == 3:
    print('EXT1 Wake-up')
    
timer3 = Timer(3)
timer3.init(period=30000,mode=Timer.PERIODIC,callback=lambda t:esp32_sleep())



