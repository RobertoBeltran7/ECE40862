
from machine import RTC
from machine import Timer
from time import sleep
from machine import ADC
from machine import Pin
import machine
from machine import PWM

global switch_press
switch_press = 0
rtc = RTC()
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)
pwm_red = PWM(Pin(26),freq=10,duty=256)
pwm_green = PWM(Pin(25),freq=10,duty=256)

switch1 = Pin(14,Pin.IN,Pin.PULL_UP)
switch2 = Pin(21,Pin.IN,Pin.PULL_UP)



#adc_pin = adc.channel(pin='A0')

year = int(input('Year? '))
month = int(input('Month? '))
day = int(input('Day? '))
weekday = int(input('Weekday? '))
hour = int(input('Hour? '))
minute = int(input('Minute? '))
second = int(input('Second? '))
microsecond = int(input('Microsecond? '))

rtc.datetime((year,month,day,weekday,hour,minute,second,microsecond))

def pDate(datetime):
    print('Date: '+ "{:02d}".format(datetime[0]) + '/' + "{:02d}".format(datetime[1]) + '/' + "{:02d}".format(datetime[2]))
    print('Time:' + "{:02d}".format(datetime[4]) + ':' + "{:02d}".format(datetime[5]) + ':' + "{:02d}".format(datetime[6]))

timer = Timer(1)
timer.init(period=30000,mode=Timer.PERIODIC,callback=lambda t:pDate(rtc.datetime()))


timer2 = Timer(-1)
timer2.init(period=100,mode=Timer.PERIODIC,callback= lambda t:adc.read())

def callback(pin):
    global switch_press
    switch_press = switch_press + 1
    sleep(0.05)
    
def callback2(pin):
    global switch_press
    switch_press = switch_press + 1
    sleep(0.05)

switch1.irq(trigger=Pin.IRQ_FALLING,handler = callback)
switch2.irq(trigger=Pin.IRQ_FALLING,handler = callback2)

while True:
    if switch_press % 2 != 0:
        pwm_red = PWM(Pin(26),freq=adc.read(),duty =256)
    elif switch_press % 2 == 0:
        pwm_green = PWM(Pin(25),freq=10,duty=adc.read())


     
