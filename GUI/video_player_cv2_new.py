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
Date          	By	Comments
----------	---	---------------------------------------------------------
"""

import sys
from tkinter.ttk import Combobox
from turtle import window_height
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
    QComboBox,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from arduino_serial import ArduinoSerial


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thermal Feedback GUI")
        self.setGeometry(100, 100, 1920, 1080)
        self.setMinimumSize(1280, 720)
        self.setStyleSheet("background-color: black; color: white; font-weight: bold;")

        self.arduino = ArduinoSerial()

        # Top control bar
        self.refresh_box = QComboBox()
        self.refresh_box.addItems(["Refresh", "Option 1", "Option 2"])
        # self.refresh_box.setStyleSheet("font-size: 10em;")
        # self.refresh_box.setFixedWidth(300)
        # self.refresh_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.port_box = QComboBox()
        _items = self.arduino.list_available_ports()
        self.port_box.addItems(_items if _items else ["No serial devices detected"])
        # self.port_box.setStyleSheet("font-size: 10em;")
        # self.port_box.setFixedWidth(300)

        self.button_btn = QPushButton("Connect")
        # self.button_btn.setStyleSheet("font-size: 10em;")
        # self.button_btn.setFixedWidth(300)
        # self.button_btn.clicked.connect(self.arduino.open_serial(port_name=self.port_box.currentText))
        # self.button_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # self.status_label = QLabel("Status")
        # self.status_label.setStyleSheet("font-size: 2em;")

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close)
        # self.exit_btn.setStyleSheet("font-size: 4em;")
        # self.exit_btn.setFixedWidth(300)
        # self.exit_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        for widget in [self.refresh_box, self.port_box, self.button_btn, self.exit_btn]:
            widget.setFixedHeight(100)
            widget.setMinimumWidth(300)
            widget.setFixedWidth(300)

            widget.setStyleSheet(
                """
                QComboBox {
                    font-size: 40px;
                    background-color: white;
                    color: black;
                    padding: 8px;
                    border: 2px solid gray;
                    border-radius: 6px;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 30px;
                    border-left-width: 1px;
                    border-left-color: darkgray;
                    border-left-style: solid;
                    border-top-right-radius: 3px;
                    border-bottom-right-radius: 3px;
                }
                QComboBox::down-arrow {
                    image: none;
                }
                QPushButton {
                    font-size: 40px;
                    background-color: white;
                    color: black;
                    border: 2px solid gray;
                    border-radius: 10px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #dddddd;
                }
            """
            )
            
        # Top bar layout
        top_bar = QHBoxLayout()

        top_bar.addWidget(self.refresh_box)
        top_bar.addWidget(self.port_box)
        top_bar.addWidget(self.button_btn)
        top_bar.addStretch()
        top_bar.addWidget(self.exit_btn)

        # Left control panel

        # 设置白底黑字样式
        common_button_style = """
            QPushButton {
                font-size: 40px;
                background-color: white;
                color: black;
                border: 2px solid gray;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #dddddd;
            }
        """

        combo_box_style = """
            QComboBox {
                font-size: 40px;
                background-color: white;
                color: black;
                border: 2px solid gray;
                border-radius: 8px;
                padding: 4px;
            }
            QComboBox QAbstractItemView {
                font-size: 1.5px;
                background-color: white;
                color: black;
                selection-background-color: #bbbbbb;
            }
        """

        label_style = """
            QLabel {
                font-size: 40px;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """
        
        self.select_label = QLabel("select video")
        self.select_label.setStyleSheet(label_style)
        self.select_combo = QComboBox()
        self.select_combo.currentIndexChanged.connect(self.load_selected_video)
        self.select_combo.setStyleSheet(combo_box_style)
        self.select_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.stimulus_label = QLabel("stimulus")
        self.stimulus_label.setStyleSheet(label_style)
        self.stimulus_btn = QPushButton("OFF")
        self.stimulus_btn.setStyleSheet(common_button_style)
        self.stimulus_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.video_label_title = QLabel("video")
        self.video_label_title.setStyleSheet(label_style)
        self.video_control_btn = QPushButton("STOP")
        self.video_control_btn.clicked.connect(self.toggle_video)
        self.video_control_btn.setStyleSheet(common_button_style)
        self.video_control_btn.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        left_panel = QVBoxLayout()
        for widget in [
            self.select_label,
            self.select_combo,
            self.stimulus_label,
            self.stimulus_btn,
            self.video_label_title,
            self.video_control_btn,
        ]:
            left_panel.addWidget(widget)
            widget.setFixedWidth(350)
            widget.setFixedHeight(100)

        left_frame = QFrame()
        left_frame.setLayout(left_panel)
        left_frame.setStyleSheet("background-color: #333333; padding: 10px;")
        left_frame.setFixedWidth(400)

        # Video display
        self.video_label = QLabel("Video Display")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(800, 600)
        self.video_label.setStyleSheet("border: 1px solid white;")
        self.video_label.setScaledContents(True)

        # Layouts
        content_layout = QHBoxLayout()
        content_layout.addWidget(left_frame)
        content_layout.addWidget(self.video_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_bar)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)

        self.cap = None
        self.fps = 30
        self.current_frame = 0
        self.annotations = []
        self.video_paths = []
        self.current_index = -1
        self.playing = False

        self.video_files = list(
            (Path(__file__).parent / "assets" / "videos").glob("*.mp4")
        )
        self.video_files = sorted(self.video_files)
        self.load_video_list()

    def pause_video(self):
        self.playing = False
        self.timer.stop()

    def load_video_list(self):
        self.select_combo.clear()
        for p in self.video_files:
            self.select_combo.addItem(p.name)
        if self.video_files:
            self.select_combo.setCurrentIndex(0)
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
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        scaled_image = qt_image.scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.video_label.setPixmap(QPixmap.fromImage(scaled_image))

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

                val = max(0, min(255, val))
                msg = f"{source}{round(val)}"
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

    def toggle_video(self):
        if self.timer.isActive():
            self.timer.stop()
            self.video_control_btn.setText("PLAY")
        else:
            self.timer.start(int(1000 / self.fps))
            self.video_control_btn.setText("STOP")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
