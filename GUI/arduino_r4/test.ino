/*
 * File: /workspace/code/GUI/arduino_r4/test.ino
 * Project: /workspace/code/GUI/arduino_r4
 * Created Date: Friday May 30th 2025
 * Author: Kaixu Chen
 * -----
 * Comment:
 * This is a simple Arduino sketch that reads input from the serial port
 * 
 * Have a good code time :)
 * -----
 * Last Modified: Friday May 30th 2025 9:36:50 am
 * Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
 * -----
 * Copyright (c) 2025 The University of Tsukuba
 * -----
 * HISTORY:
 * Date      	By	Comments
 * ----------	---	---------------------------------------------------------
 */

void setup() {
  Serial.begin(9600);  // 初始化串口通信，波特率为 9600
}

void loop() {
  if (Serial.available() > 0) {  // 如果有数据可以读取
    String input = Serial.readStringUntil('\n');  // 读取直到换行符
    Serial.print("Received: ");
    Serial.println(input);  // 打印接收到的数据
  }
}
