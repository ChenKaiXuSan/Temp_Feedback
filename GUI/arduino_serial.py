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
        """初始化串口通信"""
        print("ArduinoSerial 初始化")

        available_ports = self.list_available_ports()
        if not available_ports:
            print("⚠️ 没有检测到串口设备。")

        self.ser = self.open_serial(available_ports[0])

    @staticmethod
    def list_available_ports():
        """列出所有可用串口设备"""
        print("可用串口：")
        ports = list_ports.comports()
        for port in ports:
            print(f"  - {port.device} ({port.description})")
        return [port.device for port in ports]

    def open_serial(self, port_name, baudrate=9600, timeout=1):
        """打开串口连接"""
        try:
            ser = serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout)
            print(f"✅ 已连接：{port_name}")
            return ser
        except Exception as e:
            print(f"❌ 无法打开串口 {port_name}：{e}")
            return None

    def send_command(self, ser, message):
        """发送数据到串口"""
        if ser and ser.is_open:
            ser.write((message + "\n").encode("utf-8"))
            print(f"📤 已发送：{message.strip()}")
        else:
            print("❌ 串口未打开")

    def read_response(self, ser):
        """读取串口返回数据"""
        if ser and ser.in_waiting:
            line = ser.readline().decode("utf-8").strip()
            print(f"📥 收到：{line}")
            return line
        return None

    def __call__(self, text: str):

        # time.sleep(2)  # 等设备准备好

        try:
            self.send_command(self.ser, text)
            time.sleep(0.2)
            self.read_response(self.ser)
        except KeyboardInterrupt:
            print("no more input")

        response = self.ser.readline().decode("utf-8").strip()
        if response:
            print(f"📥 收到：{response}")
            return response
        else:
            print("❌ 没有收到数据")
            return None
            
        # finally:
        #     self.ser.close()
        #     print("🔌 串口已关闭")
