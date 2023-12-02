#!/usr/bin/python
# -*- coding: UTF-8 -*-

#
#    this is an UART-LoRa device and thers is an firmware on Module
#    users can transfer or receive the data directly by UART and dont
#    need to set parameters like coderate,spread factor,etc.
#    |============================================ |
#    |   It does not suport LoRaWAN protocol !!!   |
#    | ============================================|
#   
#    This script is mainly for Raspberry Pi 3B+, 4B, and Zero series
#    Since PC/Laptop does not have GPIO to control HAT, it should be configured by
#    GUI and while setting the jumpers, 
#    Please refer to another script pc_main.py
#

import sys
import sx126x
import threading
import time
import select
import termios
import tty
from threading import Timer
import subprocess

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())


#
#    Need to disable the serial login shell and have to enable serial interface 
#    command `sudo raspi-config`
#    More details: see https://github.com/MithunHub/LoRa/blob/main/Basic%20Instruction.md
#
#    When the LoRaHAT is attached to RPi, the M0 and M1 jumpers of HAT should be removed.
#


#    The following is to obtain the temprature of the RPi CPU 
def get_cpu_temp():
    tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp)/1000

def read_latest_label(file_path):
    # Read the last line from the file
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if lines:
            return lines[-1].strip()  # Get the last line and strip any whitespace/newline characters
        else:
            return None

# node = sx126x.sx126x(serial_num = "/dev/ttyS0",freq=433,addr=0,power=22,rssi=False,air_speed=2400,relay=False)
node = sx126x.sx126x(serial_num = "/dev/ttyS0",freq=868,addr=0,power=22,rssi=True,air_speed=2400,relay=False)

def send_label(label):
    if label:
        # Encode the label as bytes
        label_bytes = label.encode()
        addr_high = int(0)>>8  # Example high byte of address
        addr_low = int(0)&0xff   # Example low byte of address
        offset_frequence = int(868)-(850 if int(868)>850 else 410)
    #  # Example frequency offset

        # Construct the data packet
        data = bytes([addr_high]) + bytes([addr_low]) + bytes([offset_frequence]) + bytes([node.addr>>8]) + bytes([node.addr&0xff]) + bytes([node.offset_freq]) + label_bytes
            # You might want to include additional info like address or frequency
        # For simplicity, I'm sending only the label here
        node.send(data)
        print(f"Sent label: {label}")

# File path to the labels file
labels_file_path = './pred_labels.txt'

def send_deal():
    get_rec = ""
    print("")
    print("input a string such as \033[1;32m0,868,Hello World\033[0m,it will send `Hello World` to lora node device of address 0 with 868M ")
    print("please input and press Enter key:",end='',flush=True)

    while True:
        rec = sys.stdin.read(1)
        if rec != None:
            if rec == '\x0a': break
            get_rec += rec
            sys.stdout.write(rec)
            sys.stdout.flush()

    get_t = get_rec.split(",")

    offset_frequence = int(get_t[1])-(850 if int(get_t[1])>850 else 410)
    #
    # the sending message format
    #
    #         receiving node              receiving node                   receiving node           own high 8bit           own low 8bit                 own 
    #         high 8bit address           low 8bit address                    frequency                address                 address                  frequency             message payload
    data = bytes([int(get_t[0])>>8]) + bytes([int(get_t[0])&0xff]) + bytes([offset_frequence]) + bytes([node.addr>>8]) + bytes([node.addr&0xff]) + bytes([node.offset_freq]) + get_t[2].encode()

    node.send(data)
    print('\x1b[2A',end='\r')
    print(" "*200)
    print(" "*200)
    print(" "*200)
    print('\x1b[3A',end='\r')

def send_cpu_continue(continue_or_not = True):
    if continue_or_not:
        global timer_task
        global seconds
        #
        # boarcast the cpu temperature at 868.125MHz
        #
        data = bytes([255]) + bytes([255]) + bytes([18]) + bytes([255]) + bytes([255]) + bytes([12]) + "CPU Temperature:".encode()+str(get_cpu_temp()).encode()+" C".encode()
        node.send(data)
        time.sleep(0.2)
        timer_task = Timer(seconds,send_cpu_continue)
        timer_task.start()
    else:
        data = bytes([255]) + bytes([255]) + bytes([18]) + bytes([255]) + bytes([255]) + bytes([12]) + "CPU Temperature:".encode()+str(get_cpu_temp()).encode()+" C".encode()
        node.send(data)
        time.sleep(0.2)
        timer_task.cancel()
        pass

try:
    
    while True:  
        latest_label = read_latest_label(labels_file_path)
        send_label(latest_label)
        time.sleep(10)
    
        #node.receive()
        
        # timer,send messages automatically
        
except:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    # print('\x1b[2A',end='\r')
    # print(" "*100)
    # print(" "*100)
    # print('\x1b[2A',end='\r')

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
# print('\x1b[2A',end='\r')
# print(" "*100)
# print(" "*100)
# print('\x1b[2A',end='\r')
