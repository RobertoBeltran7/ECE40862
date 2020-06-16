# **ECE 40862: Software for Embedded Systems**

**Course Description:**
This course provides an introduction to software design for embedded computing systems. Major topics covered include the importance of time and timing in embedded systems, embedded software organization (FSM-based program design, polled loop systems, foreground- background systems, event driven architectures, multi-tasking, etc.), real-time scheduling and real-time operating systems, wired/wireless networked embedded systems, debugging techniques for embedded software, and advanced topics such as memory-safe programming, implementing reentrant functions, and minimizing code space, memory usage, and power consumption. The course features a series of integrated assignments using state-of-the-art embedded hardware platforms, embedded software design tools, and real-time operating systems that reinforce the concepts taught in the lectures. 

### **List of Lab Assignments**

- **Lab1: Digital Input and Output using GPIOs, LEDs, Switches**<br/>
This lab introduces GPIO with the Adafruit HUZZAH32 ESP32 Feather board using MicroPython and the Thonny IDE. The lab consists of two programs: the first blinks an onboard LED five times and the second implements a pattern function that uses two push button switches to turn on/off two external LEDs.

- **Lab2: LED control using ADC, PWM, Timers and Interrupts**<br/>
This lab introduces the ADC, PWM and RTC peripherals on the ESP32 board along with timers and interrupts. The lab implements a program that first asks the user for the current time. After the user inputs the time a hardware timer is initialized to display the current time every 30 seconds. A software timer is also initialized to read values from a potentiometer every 100 ms and PWM is initalized to blink an external LED at a frequency of 10 Hz and duty cycle of 256.

- **Lab3: Networking with Sleep and Wake-Up with Touch Sensors**<br/>
This lab introduces the on-board ESP32 touch sensor and connecting the board to the Internet. This lab implements functions to connect the ESP32 board to a Wi-Fi network ussing 'SSID' and 'Password'. Once connected, the board displays the current date and time retrieved from an NTP server. The program also implements three different wake up sources for the board either from a timer wake up, touch-based wake up or an external push button wakeup.

- **Lab4: HTTP Web Server and Client using ESP32**<br/>
This lab introduces Internet of Things(IoT) concepts by implementing client-server communication using socket APIs and HTTP protocol. The lab implements an HTTP client using the ESP32 board to read temperature/Hall sensor data and send the data to the ThingSpeak IoT Platform. It also implements an ESP32 HTTP server that displays the latest temperature, Hall sensor and two LED readings on the ESP32 server webpage. 

- **Lab5: Implementing a Flying Car using Accelerometer Sensors**<br/>
This lab introduces the use of I2C on the ESP32 board with the Adafruit Sensor Featherwing which contains a triple-axis accelerometer and temperature sensor. The lab implements a program that uses the accelerometer readings to calculate velocties and tilt angles of the board. The program also uses PWM and the temperature readings to change the frequency of an external LED for every one degree change in temperature.

- **Lab6: Secure Communication between 2 ESP32-Sensor FeatherWing Assembly/Uploading Data to Google Sheets using IFTTT**<br/>
This lab introduces MQTT communication protocol, encryption and decryption using AES and authentication using HMAC SHA with the ESP32 board. This lab uses two ESP32 boards to exchange sensor data using MQTT communication protocol. The data sent by the two boards is encrypted using AES-CBC and used to generate HMACs that one of the the boards will use to authenticate the transfer of data between the boards. The data along with the session ID is sent to Google Sheets using the IFTT service.
