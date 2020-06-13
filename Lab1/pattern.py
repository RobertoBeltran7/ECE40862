from machine import Pin
from time import sleep

red_led = Pin(26,Pin.OUT)
green_led = Pin(25,Pin.OUT)

read_input = Pin(21,Pin.IN)
read_input2 = Pin(14,Pin.IN)

test_switch2 = Pin(15,Pin.IN,Pin.PULL_UP)
switch2 = Pin(32,Pin.OUT)
#print('1.switch2 val:',test_switch2.value())
#test_switch2.off()
red_led.on()
green_led.off()
#test_switch2.on()

i = 0
j=0
while True:
    if read_input.value() == 1 and read_input2.value() == 0:
        red_led.off()
        green_led.on()
    elif read_input.value() == 1:
        sleep(0.0005)

        i+=1
    elif read_input2.value() == 0:
        sleep(0.0005)
        j+=1
    elif i>=10 or j>=10:
        read_input.init(Pin.OUT)
        read_input2.init(Pin.OUT)
        red_led.init(Pin.IN)
#         green_led.init(Pin.IN)
        
        while True:
            read_input.value(not read_input.value())
            read_input2.value(read_input.value())
            sleep(0.0005)
            if i>=10 and green_led.value() and read_input.value():
                read_input.off()
                read_input2.on()
                break
            elif j>=10 and red_led.value() and read_input.value():
                read_input.off()        
                read_input2.on()
                break
        break
print('You have successfully implemented LAB1 DEMO!!!')
#if green_led.value() == 0:
#    print('Push button 2 is pressed')