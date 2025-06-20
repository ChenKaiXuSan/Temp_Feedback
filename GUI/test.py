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
Updated to mimic the GUI design shown in the given reference image.
Now integrates full video playback using OpenCV.

Have a good code time :)
-----
Last Modified: Friday May 30th 2025 9:36:50 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2025 The University of Tsukuba
-----
HISTORY:
Date           	By	Comments
----------	---	---------------------------------------------------------
"""

import sys
import cv2
import json
import re
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QComboBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from arduino_serial import ArduinoSerial


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thermal Feedback GUI")
        self.setGeometry(100, 100, 1280, 720)
        self.setStyleSheet("background-color: black; color: white; font-weight: bold;")

        self.arduino = ArduinoSerial()

        # Top control bar
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet("font-size: 1.5em;")

        self.port_box = QComboBox()
        self.port_box.addItems(["COM4", "COM5", "COM6"])
        self.port_box.setStyleSheet("font-size: 1.5em;")

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setStyleSheet("font-size: 1.5em;")

        self.status_label = QLabel("status")
        self.status_label.setStyleSheet("font-size: 1.5em;")

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.setStyleSheet("font-size: 1.5em;")
        self.exit_btn.clicked.connect(self.close)

        top_bar = QHBoxLayout()
        for w in [self.refresh_btn, self.port_box, self.connect_btn, self.status_label, self.exit_btn]:
            top_bar.addWidget(w)

        # Left control panel
        self.select_label = QLabel("Select video")
        self.select_label.setStyleSheet("font-size: 1.5em;")

        self.select_combo = QComboBox()
        self.select_combo.setStyleSheet("font-size: 1.5em;")
        self.select_combo.currentIndexChanged.connect(self.load_selected_video)

        self.stimulus_label = QLabel("stimulus")
        self.stimulus_label.setStyleSheet("font-size: 1.5em;")
        self.stimulus_btn = QPushButton("OFF")
        self.stimulus_btn.setStyleSheet("font-size: 1.5em;")

        self.video_label_title = QLabel("video")
        self.video_label_title.setStyleSheet("font-size: 1.5em;")
        self.video_control_btn = QPushButton("STOP")
        self.video_control_btn.setStyleSheet("font-size: 1.5em;")
        self.video_control_btn.clicked.connect(self.toggle_video)

        left_panel = QVBoxLayout()
        for widget in [self.select_label, self.select_combo, self.stimulus_label,
                       self.stimulus_btn, self.video_label_title, self.video_control_btn]:
            left_panel.addWidget(widget)
            widget.setFixedWidth(120)

        left_frame = QFrame()
        left_frame.setLayout(left_panel)
        left_frame.setStyleSheet("background-color: #333333; padding: 10px;")
        left_frame.setFixedWidth(150)

        # Video area
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("border: 1px solid white;")
        self.video_label.setScaledContents(True)

        content_layout = QHBoxLayout()
        content_layout.addWidget(left_frame)
        content_layout.addWidget(self.video_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_bar)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

        # Video playback logic
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.fps = 30
        self.current_frame = 0
        self.annotations = []

        self.video_files = sorted((Path(__file__).parent / "assets" / "videos").glob("*.mp4"))
        self.load_video_list()

    def load_video_list(self):
        self.select_combo.clear()
        for p in self.video_files:
            self.select_combo.addItem(p.name)
        if self.video_files:
            self.load_selected_video()

    def load_selected_video(self):
        index = self.select_combo.currentIndex()
        if 0 <= index < len(self.video_files):
            if self.cap:
                self.cap.release()
            path = str(self.video_files[index])
            self.cap = cv2.VideoCapture(path)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            self.timer.start(int(1000 / self.fps))
            self.load_llm_res(path)

    def load_llm_res(self, path):
        json_file = Path(path).stem + ".json"
        json_path = Path(__file__).parent / "assets" / "llm_res" / json_file
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self.annotations = json.load(f)
        except:
            self.annotations = []

    def toggle_video(self):
        if self.timer.isActive():
            self.timer.stop()
            self.video_control_btn.setText("PLAY")
        else:
            self.timer.start(int(1000 / self.fps))
            self.video_control_btn.setText("STOP")

    def next_frame(self):
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image.scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)))

        if self.current_frame % int(self.fps) == 0:
            result = self.find_res_with_position(self.current_frame)
            if result:
                source = result["source"][0]
                proportion = result["proportion"]
                if source == "h":
                    val = int(proportion * 255)
                elif source == "c":
                    val = int(proportion * 70 + 185)
                else:
                    val = 0
                msg = f"{source}{max(0, min(255, val))}"
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
