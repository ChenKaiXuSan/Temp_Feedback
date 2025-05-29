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
