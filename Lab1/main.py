from machine import Pin
from time import sleep

led_board = Pin(13,Pin.OUT)

for i in range(10):
    led_board.value(not led_board.value())
    sleep(0.5)
    
print("Led blinked 5 times")