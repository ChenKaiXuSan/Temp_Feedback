import sys
import json
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QSlider,
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QTime


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频播放器 + 注释显示")
        self.setGeometry(100, 100, 1000, 600)

        # 播放器组件
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setNotifyInterval(100)

        self.videoWidget = QVideoWidget()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.mediaPlayer.setPosition)

        self.timeLabel = QLabel("00:00 / 00:00")
        self.timeLabel.setAlignment(Qt.AlignRight)
        self.annotationLabel = QLabel("🔍 注释区")
        self.annotationLabel.setStyleSheet(
            "font-weight: bold; font-size: 16px; color: darkblue"
        )

        # 控制按钮
        openBtn = QPushButton("打开视频")
        openBtn.clicked.connect(self.open_file)

        playBtn = QPushButton("播放")
        playBtn.clicked.connect(self.mediaPlayer.play)

        pauseBtn = QPushButton("暂停")
        pauseBtn.clicked.connect(self.mediaPlayer.pause)

        stopBtn = QPushButton("停止")
        stopBtn.clicked.connect(self.mediaPlayer.stop)

        # 布局
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(openBtn)
        btnLayout.addWidget(playBtn)
        btnLayout.addWidget(pauseBtn)
        btnLayout.addWidget(stopBtn)

        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        layout.addWidget(self.slider)
        layout.addWidget(self.timeLabel)
        layout.addWidget(self.annotationLabel)
        layout.addLayout(btnLayout)

        self.setLayout(layout)

        # 信号连接
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.durationChanged.connect(self.slider.setMaximum)
        self.mediaPlayer.positionChanged.connect(self.update_position)

        # 注释数据
        self.annotations = []
        self.current_annotation = ""

        # 加载 JSON 注释
        self.load_annotations("annotations.json")

    def open_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "选择视频文件")
        if fileName:
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.mediaPlayer.play()

    def load_annotations(self, json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self.annotations = json.load(f)
            print(f"✅ 成功加载注释：{len(self.annotations)} 条")
        except Exception as e:
            print(f"❌ 加载注释失败: {e}")
            self.annotations = [
                {"start": 0, "end": 5000, "text": "🎬 介绍开始"},
                {"start": 5000, "end": 10000, "text": "🚪 场景进入"},
                {"start": 10000, "end": 20000, "text": "🔥 高潮部分"},
                {"start": 20000, "end": 60000, "text": "🎉 结尾总结"},
            ]

    def update_position(self, position):
        self.slider.setValue(position)

        # 更新时间标签
        current_time = QTime(0, 0, 0).addMSecs(position)
        total_time = QTime(0, 0, 0).addMSecs(self.mediaPlayer.duration())
        self.timeLabel.setText(
            f"{current_time.toString('mm:ss')} / {total_time.toString('mm:ss')}"
        )

        # 查找注释信息
        matched = ""
        for ann in self.annotations:
            if ann["start"] <= position < ann["end"]:
                matched = ann["text"]
                break

        if matched != self.current_annotation:
            self.annotationLabel.setText(matched)
            self.current_annotation = matched


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
