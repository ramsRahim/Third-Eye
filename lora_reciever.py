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

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

node = sx126x.sx126x(serial_num = "/dev/ttyS0",freq=868,addr=0,power=22,rssi=True,air_speed=2400,relay=False)
def receive_and_decode():
    # Receive data from LoRa
    data = node.receive()
    
    if data:
        # Decode the data structure
        recv_node_high = data[0]
        recv_node_low = data[1]
        offset_frequence = data[2]
        send_node_high = data[3]
        send_node_low = data[4]
        offset_freq_sender = data[5]

        # Reconstruct the addresses and the message
        recv_node_addr = (recv_node_high << 8) | recv_node_low
        send_node_addr = (send_node_high << 8) | send_node_low
        message = data[6:].decode('utf-8', errors='ignore')  # Decoding the message as UTF-8

        print(f"Received message: {message}")
        print(f"From node address: {send_node_addr}")
        print(f"To node address: {recv_node_addr}")

# Main loop to continuously receive data
    
try:
    print("The receiver is listening ...")
    while True:        
        receive_and_decode()
        
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
