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

import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 不使用 GUI backend
from io import BytesIO

import cv2
import matplotlib.pyplot as plt
import numpy as np
from arduino_serial import ArduinoSerial
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,  # 新增
    QPushButton,
    QSizePolicy,
    QStackedLayout,  # 新增
    QVBoxLayout,
    QWidget,
)


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thermal Feedback GUI")
        self.setGeometry(100, 100, 1920, 1080)
        self.setMinimumSize(1280, 720)
        self.setStyleSheet("background-color: black; color: white; font-weight: bold;")

        self.arduino = ArduinoSerial()

        # top control panel

        self.select_label = QLabel("select video")
        self.select_label.setStyleSheet("font-size: 10em;")

        self.select_combo = QComboBox()
        self.select_combo.currentIndexChanged.connect(self.load_selected_video)
        self.select_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.video_control_btn = QPushButton("STOP")
        self.video_control_btn.clicked.connect(self.toggle_video)
        self.video_control_btn.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close)

        for widget in [
            self.exit_btn,
            self.select_label,
            self.select_combo,
            self.video_control_btn,
        ]:
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

        top_bar.addStretch()
        top_bar.addWidget(self.select_label)
        top_bar.addWidget(self.select_combo)
        top_bar.addWidget(self.video_control_btn)
        top_bar.addWidget(self.exit_btn)

        # Video display (实际播放区域)
        self.video_label = QLabel("Video Display")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(800, 600)
        self.video_label.setStyleSheet("border: 1px solid white;")
        self.video_label.setScaledContents(True)

        # analysis display
        self.analysis_label = QLabel("Analysis Display")
        self.analysis_label.setAlignment(Qt.AlignCenter)
        self.analysis_label.setMinimumSize(800, 600)
        self.analysis_label.setStyleSheet("border: 1px solid white;")
        self.analysis_label.setScaledContents(True)

        # ---- 新增：加载中的界面 ----
        self.loading_label = QLabel("Processing selected video...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: white; font-size: 32px;")

        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)  # 0,0 = 不确定进度的滚动条
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setFixedHeight(40)
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid gray;
                border-radius: 5px;
                background-color: #222222;
            }
            QProgressBar::chunk {
                background-color: #00aa00;
                width: 20px;
            }
        """)

        loading_layout = QVBoxLayout()
        loading_layout.addStretch()
        loading_layout.addWidget(self.loading_label)
        loading_layout.addWidget(self.loading_bar)
        loading_layout.addStretch()

        self.loading_widget = QWidget()
        self.loading_widget.setLayout(loading_layout)

        # 视频显示页
        video_page_layout = QVBoxLayout()
        video_page_layout.addWidget(self.video_label)
        self.video_widget = QWidget()
        self.video_widget.setLayout(video_page_layout)

        # 分析结果显示页
        analysis_page_layout = QVBoxLayout()
        analysis_page_layout.addWidget(self.analysis_label)
        self.analysis_widget = QWidget()
        self.analysis_widget.setLayout(analysis_page_layout)

        # 用 QStackedLayout 切换两种界面
        self.stack = QStackedLayout()
        self.stack.addWidget(self.loading_widget)  # index 0
        self.stack.addWidget(self.video_widget)  # index 1
        self.stack.setCurrentIndex(1)  # 默认显示视频页（初始时无加载）

        # Layouts
        content_layout = QHBoxLayout()
        content_layout.addLayout(self.stack)
        content_layout.addWidget(self.analysis_widget)

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
            # (Path(__file__).parent / "assets" / "videos").glob("*.mp4")
            (self.resource_path("assets") / "videos").glob("*.mp4")
        )
        self.video_files = sorted(self.video_files)
        self.load_video_list()

        self.analysis_res_draw = []

    def resource_path(self, rel_path: str | Path) -> Path:
        """
        返回打包后可用的资源绝对路径。
        - onefile: 使用 sys._MEIPASS
        - 开发时: 相对当前文件所在目录
        """
        base_path = getattr(sys, "_MEIPASS", None)
        if base_path:
            base = Path(base_path)
        else:
            # 根据你的需要选择项目根或当前文件目录
            base = Path(__file__).resolve().parent

        return base / rel_path

    def show_loading(self, loading: bool):
        """
        True: 显示“Processing...”界面
        False: 显示视频播放界面
        """
        if loading:
            self.stack.setCurrentIndex(0)
        else:
            self.stack.setCurrentIndex(1)

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
            # 先切到“Processing...”界面
            self.show_loading(True)

            path = str(self.video_files[index])

            # 用 singleShot 把真正的工作放到事件循环的下一拍执行
            # 这样界面会先刷新出 loading 画面
            # 这里控制延时 2 秒模拟处理时间
            QTimer.singleShot(2000, lambda p=path: self._open_video(p))

    def _open_video(self, path: str):
        # 真正的“加载视频 + 初始化播放”的逻辑
        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30

        # （如果后面你有更重的预处理，比如读取所有帧、跑推理，
        #  可以在这里加入循环，同时适当手动更新一个百分比进度）

        self.load_llm_res(path)
        self.timer.start(int(1000 / self.fps))

        # 加载完成，切回视频界面
        self.show_loading(False)

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
                    # val = int(proportion * 255)
                    val = int(proportion * 80 + 150)
                elif source == "c":
                    val = int(proportion * 70 + 185)
                else:
                    val = 0

                val = max(0, min(255, val))
                msg = f"{source}{round(val)}"

                self.analysis_res_draw.append(source)

                self.arduino(msg)

    def draw_analysis_result(self):
        data = self.analysis_res_draw
        if not data or len(data) < 2:
            self.analysis_label.setText("No data")
            return

        # ------------------ 1. 用 Matplotlib 画图 ------------------
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)

        ax.plot(data, color="green", linewidth=3)
        ax.set_facecolor("black")
        fig.patch.set_facecolor("black")

        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["top"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["right"].set_color("white")

        ax.set_title("Analysis Curve", color="white")
        ax.set_xlabel("Index", color="white")
        ax.set_ylabel("Value", color="white")

        fig.tight_layout()

        # ------------------ 2. 保存到内存 Buffer ------------------
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)  # 关闭 Matplotlib 图形窗口

        # ------------------ 3. 转成 QImage / QPixmap ------------------
        qimg = QImage.fromData(buf.getvalue(), "PNG")
        pixmap = QPixmap.fromImage(qimg)

        # 自动缩放到 QLabel 大小
        pixmap = pixmap.scaled(
            self.analysis_label.width(),
            self.analysis_label.height(),
            aspectRatioMode=Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation,
        )

        # ------------------ 4. 显示到 QLabel ------------------
        self.analysis_label.setPixmap(pixmap)

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
