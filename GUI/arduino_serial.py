#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: /home/chenkaixu/Temp_Feedback/GUI/serial.py
Project: /home/chenkaixu/Temp_Feedback/GUI
Created Date: Sunday May 25th 2025
Author: Kaixu Chen
-----
Comment:

Have a good code time :)
-----
Last Modified: Sunday May 25th 2025 8:46:00 pm
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2025 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""
import serial
import time
from serial.tools import list_ports


class ArduinoSerial:

    def __init__(self):
        """Initialize serial communication"""
        print("ArduinoSerial initializing...")

        available_ports = self.list_available_ports()
        if not available_ports:
            print("⚠️ No serial devices detected.")
            self.ser = None
            return

        # Step 1: Select serial port
        print("\nPlease select a serial port:")
        for idx, port in enumerate(available_ports):
            print(f"[{idx}] {port}")
        while True:
            try:
                port_choice = input("Enter port index (default 0): ") or "0"
                port_choice = int(port_choice)
                if 0 <= port_choice < len(available_ports):
                    break
                else:
                    print("❌ Invalid index, please try again.")
            except ValueError:
                print("❌ Please enter a valid integer.")

        selected_port = available_ports[port_choice]

        # Step 2: Let user input baudrate manually

        while True:
            try:
                baud_input = input("Enter baudrate (default 9600): ") or "9600"
                baudrate = int(baud_input)
                if baudrate > 0:
                    break
                else:
                    print("❌ Baudrate must be a positive number.")
            except ValueError:
                print("❌ Please enter a valid integer baudrate.")
                
        self.ser = self.open_serial(selected_port, baudrate=baudrate, timeout=1)

    @staticmethod
    def list_available_ports():
        """List all available serial ports"""
        print("Available serial ports:")
        ports = list_ports.comports()
        for port in ports:
            print(f"  - {port.device} ({port.description})")
        return [port.device for port in ports]

    def open_serial(self, port_name, baudrate=9600, timeout=1):
        """Open the serial connection"""
        try:
            ser = serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout)
            print(f"✅ Connected to: {port_name}")
            return ser
        except Exception as e:
            print(f"❌ Failed to open port {port_name}: {e}")
            return None

    def send_command(self, ser, message):
        """Send a message to the serial port"""
        if ser and ser.is_open:
            ser.write((message + "\n").encode("utf-8"))
            print(f"📤 Sent: {message.strip()}")
        else:
            print("❌ Serial port is not open")

    def read_response(self, ser):
        """Read response from the serial port"""
        if ser and ser.in_waiting:
            line = ser.readline().decode("utf-8").strip()
            print(f"📥 Received: {line}")
            return line
        return None

    def __call__(self, text: str):

        # time.sleep(2)  # Wait for the device to be ready

        try:
            self.send_command(self.ser, text)
            time.sleep(0.2)
            self.read_response(self.ser)
        except KeyboardInterrupt:
            print("No more input")

        # finally:
        #     self.ser.close()
        #     print("🔌 Serial port closed")
