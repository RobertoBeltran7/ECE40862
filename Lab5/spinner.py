import machine
from machine import Pin
from machine import I2C
from machine import Timer
from machine import PWM
from math import atan
from math import degrees
from math import pow
from math import sqrt

global redLED
redLED = Pin(13, Pin.OUT)
global redExtLED
redExtLED = Pin(33, Pin.OUT)
global yellowLED
yellowLED = Pin(27, Pin.OUT)
global greenLED
greenLED = Pin(12, Pin.OUT)


def temp_c(data):
    value = data[0] << 8 | data[1]
    temp = (value & 0x7FFF) / 128.0
    
    if value & (1<<15):
        temp -= 256.0
    return temp

def convertTo2Comp(data):
    neg = False
    if (data & (1<<15)) != 0:
        neg = True
    d = ~data
    d += 1
    if neg:
        d = -1 * d
    return d

def b1_action():
    print("B1 Pressed")
    redLED.value(1)
    i2c = I2C(1, scl=Pin(22), sda=Pin(23), freq=40000)
    print(i2c.scan())
    if len(i2c.scan()) == 0:
      print("Error, can't detect addresses")
      return
    if (72 not in i2c.scan()) or (83 not in i2c.scan()):
        print("Error, Incorrect addresses")
        return
    temp_address = i2c.scan()[0] #72
    acce_address = i2c.scan()[1] #83
    temp_reg = 3
    res_reg = 8
    i2c.writeto_mem(temp_address, temp_reg, b'\x80')
    print("Temperature Sensor initialized to 16-bit Resolution")
    acc_reg = 49
    i2c.writeto_mem(acce_address, acc_reg, b'\x06')
    acc_reg = 0x2C
    i2c.writeto_mem(acce_address, acc_reg, b'\x0D')
    acc_reg = 0x2D
    i2c.writeto_mem(acce_address, acc_reg, b'\x08')
    acc_reg = 0x1E
    i2c.writeto_mem(acce_address, acc_reg, b'\x00')
    acc_reg = 0x1F
    i2c.writeto_mem(acce_address, acc_reg, b'\x00')
    acc_reg = 0x20
    i2c.writeto_mem(acce_address, acc_reg, b'\x00')
    print("Accelerometer calibrated")

    
def b1_interrupt(p4):
    tim = Timer(1)
    tim.init(mode=Timer.ONE_SHOT, period = 100, callback=lambda t:b1_action())
    
def b2_action():
    redLED.value(0)
    print("B2 pressed")
    offsetx = bytearray(1)
    offsety = bytearray(1)
    offsetz = bytearray(1)
    
    i2c = I2C(1, scl=Pin(22), sda=Pin(23), freq=40000)
    if len(i2c.scan()) == 0:
      print("Error, can't detect addresses")
      return
    if (72 not in i2c.scan()) or (83 not in i2c.scan()):
        print("Error, Incorrect addresses")
        return
    temp_address = i2c.scan()[0] #72
    acce_address = i2c.scan()[1] #83
    
    i2c.readfrom_mem_into(acce_address, 0x1E, offsetx)
    i2c.readfrom_mem_into(acce_address, 0x1F, offsety)
    i2c.readfrom_mem_into(acce_address, 0x20, offsetz)
    
    temp = bytearray(2)
    accel = bytearray(6)
    
    i2c.readfrom_mem_into(acce_address, 0x32, accel)
    
    Ax0 = convertTo2Comp(accel[1] << 8 | accel[0])
    Ay0 = convertTo2Comp(accel[2] << 8 | accel[2])  
    Az0 = convertTo2Comp(accel[5] << 8 | accel[4])  

    Vx0 = 0
    Vy0 = 0
    Vz0 = 0
    pwm = PWM(Pin(13), freq=10, duty=512)
    i2c.readfrom_mem_into(temp_address, 0x00, temp)
    tempinitVal = temp_c(temp)
    while True:
        i2c.readfrom_mem_into(temp_address, 0x00, temp)
        tempVal = temp_c(temp)
        print("Current Temperature is " + str(tempVal) + " degree Celsius")
        if tempVal - tempinitVal >= 1:
            pwm.freq(pwm.freq() + 5)
            
        if tempVal - tempinitVal <= -1:
            pwm.freq(pwm.freq() - 5)
        tempinitVal = tempVal
        
        i2c.readfrom_mem_into(acce_address, 0x32, accel)
        
        
        Ax = convertTo2Comp(accel[1] << 8 | accel[0])
        Ay = convertTo2Comp(accel[3] << 8 | accel[2])  
        Az = convertTo2Comp(accel[5] << 8 | accel[4])
        
        Vx0 += (Ax) * 0.001
        Vy0 += (Ay) * 0.001
        Vz0 += (Az - 9.81) * 0.001
        
        print("velocity in X axis is " + str(Vx0))
        print("velocity in Y axis is " + str(Vy0))
        print("velocity in Z axis is " + str(Vz0))
        
        if(abs(Vx0) > 4 or abs(Vy0) > 4 or abs(Vz0) > 4):
            redExtLED.value(1)
        else:
            redExtLED.value(0)
           
        pitch = degrees(atan(Ax/sqrt(pow(Ay, 2) + pow(Az, 2)))) 
        roll = degrees(atan(Ay/sqrt(pow(Ax, 2) + pow(Az, 2))))
        theta = degrees(atan(sqrt(pow(Ax, 2) + pow(Ay, 2)) / Az))
        if abs(pitch) > 30 or abs(roll) > 30 or abs(theta) > 30:
            yellowLED.value(1)
        else:
            yellowLED.value(0)
        print("Pitch is " + str(pitch))
        print("Roll is " + str(roll))
        print("Theta is " + str(theta))
        
        if Vx0 == 0.0 and Vy0 == 0.0 and Vz0 == 0.0 and pitch == 0.0 and roll == 0.0 and theta == 0.0:
            greenLED.value(1)
        else:
            greenLED.value(0)
    
def b2_interrupt(p21):
    tim = Timer(2)
    tim.init(mode=Timer.ONE_SHOT, period = 100, callback=lambda t:b2_action())
    
    
if __name__ == "__main__":

  p4 = Pin(4, Pin.IN, Pin.PULL_DOWN)
  p21 = Pin(21, Pin.IN, Pin.PULL_DOWN)
  p4.irq(trigger=Pin.IRQ_RISING, handler = b1_interrupt)
  p21.irq(trigger=Pin.IRQ_RISING, handler = b2_interrupt)
  
  
  
  