#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
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
'''
import serial
import time
from serial.tools import list_ports


def list_available_ports():
    """列出所有可用串口设备"""
    print("可用串口：")
    ports = list_ports.comports()
    for port in ports:
        print(f"  - {port.device} ({port.description})")
    return [port.device for port in ports]


def open_serial(port_name, baudrate=9600, timeout=1):
    """打开串口连接"""
    try:
        ser = serial.Serial(
            port=port_name,
            baudrate=baudrate,
            timeout=timeout
        )
        print(f"✅ 已连接：{port_name}")
        return ser
    except Exception as e:
        print(f"❌ 无法打开串口 {port_name}：{e}")
        return None


def send_command(ser, message):
    """发送数据到串口"""
    if ser and ser.is_open:
        ser.write((message + '\n').encode('utf-8'))
        print(f"📤 已发送：{message.strip()}")
    else:
        print("❌ 串口未打开")


def read_response(ser):
    """读取串口返回数据"""
    if ser and ser.in_waiting:
        line = ser.readline().decode('utf-8').strip()
        print(f"📥 收到：{line}")
        return line
    return None


def main():
    print("=== 串口通信示例 ===")
    available_ports = list_available_ports()
    if not available_ports:
        print("⚠️ 没有检测到串口设备。")
        return

    port_name = input(f"请输入串口名称（例如 {available_ports[0]}）：").strip()
    ser = open_serial(port_name)

    if not ser:
        return

    time.sleep(2)  # 等设备准备好

    try:
        while True:
            cmd = input("请输入要发送的内容（输入 quit 退出）： ").strip()
            if cmd.lower() == 'quit':
                break
            send_command(ser, cmd)
            time.sleep(0.2)
            read_response(ser)
    finally:
        ser.close()
        print("🔌 串口已关闭")


if __name__ == '__main__':
    main()
