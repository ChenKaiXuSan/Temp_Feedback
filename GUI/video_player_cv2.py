#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: /workspace/code/GUI/video_player_cv2.py
Project: /workspace/code/GUI
Created Date: Friday May 30th 2025
Author: Kaixu Chen
-----
Comment:

This is a simple video player using OpenCV and PyQt5.
It allows you to open multiple video files, play, pause, and stop them.
It also integrates with an Arduino serial interface to send messages based on video frame annotations.

Have a good code time :)
-----
Last Modified: Friday May 30th 2025 9:36:50 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2025 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""

import sys
import cv2
import json
import re
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QListWidget,
    QLabel,
    QSlider,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from arduino_serial import ArduinoSerial


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 1000, 600)

        self.arduino = ArduinoSerial()

        self.video_label = QLabel("Video Display")
        self.video_label.setFixedSize(640, 480)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        self.timeLabel = QLabel("0 / 0")
        self.timeLabel.setAlignment(Qt.AlignRight)
        self.listWidget = QListWidget()
        self.listWidget.itemDoubleClicked.connect(self.play_selected_file)

        self.label = QLabel("Currently Playing:")
        self.frame_label = QLabel("Current Frame:")

        # Create buttons for video control
        openBtn = QPushButton("Open Folder")
        openBtn.clicked.connect(self.open_files)
        playBtn = QPushButton("Play")
        playBtn.clicked.connect(self.play_video)
        pauseBtn = QPushButton("Pause")
        pauseBtn.clicked.connect(self.pause_video)
        stopBtn = QPushButton("Stop")
        stopBtn.clicked.connect(self.stop_video)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(openBtn)
        btnLayout.addWidget(playBtn)
        btnLayout.addWidget(pauseBtn)
        btnLayout.addWidget(stopBtn)

        videoLayout = QVBoxLayout()
        videoLayout.addWidget(self.video_label)
        videoLayout.addWidget(self.slider)
        videoLayout.addWidget(self.timeLabel)
        videoLayout.addWidget(self.label)
        videoLayout.addWidget(self.frame_label)
        videoLayout.addLayout(btnLayout)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.listWidget, 2)
        mainLayout.addLayout(videoLayout, 5)
        self.setLayout(mainLayout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)

        self.cap = None
        self.fps = 30
        self.current_frame = 0
        self.annotations = []
        self.video_paths = []
        self.current_index = -1
        self.playing = False

        self.get_default_videos()

    def open_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "select one or more video files")
        if files:
            self.video_paths = files
            self.listWidget.clear()
            for path in files:
                self.listWidget.addItem(Path(path).name)
            self.current_index = 0
            self.load_and_play(self.current_index)

    def get_default_videos(self):
        """Load default video files from the assets/videos directory."""
        
        _path = Path(__file__).parent / "assets" / "videos"
        path_list = sorted(str(p) for p in _path.glob("*.mp4"))
        self.video_paths = path_list
        self.listWidget.clear()
        for path in path_list:
            self.listWidget.addItem(Path(path).name)
        self.current_index = 0
        self.load_and_play(self.current_index)

    def play_selected_file(self, item):
        self.current_index = self.listWidget.row(item)
        self.load_and_play(self.current_index)

    def load_and_play(self, index):
        if 0 <= index < len(self.video_paths):
            path = self.video_paths[index]
            self.cap = cv2.VideoCapture(path)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            self.slider.setMaximum(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)))
            self.load_llm_res(path)
            self.label.setText(f"Currently Playing: {Path(path).name}")
            self.current_frame = 0
            self.play_video()

    def load_llm_res(self, path):
        json_file = Path(path).stem + ".json"
        json_path = Path(__file__).parent / "assets" / "llm_res" / json_file
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self.annotations = json.load(f)
        except:
            self.annotations = []

    def play_video(self):
        self.playing = True
        interval = int(1000 / self.fps)
        self.timer.start(interval)

    def pause_video(self):
        self.playing = False
        self.timer.stop()

    def stop_video(self):
        self.pause_video()
        self.current_frame = 0
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def set_position(self, frame):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
            self.current_frame = frame
            self.next_frame()

    def next_frame(self):
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if not ret:
            self.pause_video()
            return

        self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

        self.slider.setValue(self.current_frame)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.timeLabel.setText(f"{self.current_frame} / {total_frames}")
        self.frame_label.setText(
            f"Current Frame: {self.current_frame}, ms: {1000 * self.current_frame / self.fps:.2f}"
        )

        # every fps seconds, check for annotations
        if self.current_frame % int(self.fps) == 0:
            result = self.find_res_with_position(self.current_frame)
            if result:
                msg = f"{result['source'][0]}{result['proportion'] * 255}"
                # print(msg)
                self.arduino(msg)

    def find_res_with_position(self, frame_idx):
        for info in self.annotations:
            if info.get("frame_idx") == frame_idx:
                return self.convert_str_dict(info.get("output_text"))
        return None

    def convert_str_dict(self, llm_res):
        match = re.search(r"\{.*?\}", llm_res[0], re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {"source": "none", "proportion": "none", "location": "none"}


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
