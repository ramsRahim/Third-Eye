import serial
from time import sleep
import RPi.GPIO as GPIO

# Setup Signal LED
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

red = 22
blue = 16

GPIO.setup(red, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(blue, GPIO.OUT, initial=GPIO.LOW)

# Attach Lora Module to UART pins on Pi (8 & 10)
lora = serial.Serial("/dev/ttyS0", 115200)

alarmState = False
string = ''

try:
        while True:
                print("Polling For Input...")
                # If we have incoming data, read it
                if lora.inWaiting() > 0:
                        data = lora.readline()

                        # If the incoming data isn't empty, see if it triggers an alarm
                        if (data != ''):
                                final = data.decode('utf-8')
                                # If we receive "alarm", trigger alarm state
                                print("RECEIVED: {}".format(final)) # Prints "+RCV=0,6,alarm,-45,53"
                                sleep(1)
                                data = ''
                                # Commented out for triggering Error: "[Errno 5] Input/output error"
                                #lora.flushInput()

                                # If received message contains "alarm", trigger Alarm
                                if "alarm" in final:
                                        alarmState = True
                                        print("ALARM STATE")
                                        GPIO.output(blue, GPIO.HIGH)
                                        GPIO.output(red, GPIO.LOW)
                                        string = "AT+SEND=0,6,alarm"
                                        lora.write(string.encode("utf-8"))
                                        final = ''


                if (alarmState):
                        sleep(1)
                        # Give option to clear alarm in terminal
                        output = input("Clear State? (y): ")

                        if (output == "y"):
                                string = "AT+SEND=0,6,clear\r" # Sends "clear" to clear alarm state
                                lora.write(string.encode("utf-8"))
                                alarmState = False
                                string = ""
                                output = ""
                                GPIO.output(red, GPIO.HIGH)
                                GPIO.output(blue, GPIO.LOW)
                                continue
                        elif (output == 'exit'):
                                lora.close()
                                exit()
                        else:
                                output = ''
                sleep(1)

except KeyboardInterrupt:
        print("\rExiting...")
        GPIO.output(red, GPIO.HIGH)
        GPIO.output(blue, GPIO.HIGH)