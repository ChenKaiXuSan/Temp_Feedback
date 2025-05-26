import pathlib
import sys
from turtle import position
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
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QTime


from pathlib import Path
import json
import cv2


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 1000, 600)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setNotifyInterval(100)

        self.videoWidget = QVideoWidget()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.mediaPlayer.setPosition)

        self.timeLabel = QLabel("00:00 / 00:00")
        self.timeLabel.setAlignment(Qt.AlignRight)
        self.timeLabel.setStyleSheet("color: gray; font-family: monospace;")

        self.listWidget = QListWidget()
        self.listWidget.itemDoubleClicked.connect(self.play_selected_file)

        self.label = QLabel("Currently Playing:")
        self.label.setStyleSheet("font-weight: bold;")

        self.frame_label = QLabel("Current Frame:")
        self.frame_label.setStyleSheet("font-weight: bold;")

        # load from default video files
        self.get_default_videos()

        openBtn = QPushButton("Open Folder")
        openBtn.clicked.connect(self.open_files)

        playBtn = QPushButton("Play")
        playBtn.clicked.connect(self.mediaPlayer.play)

        pauseBtn = QPushButton("Pause")
        pauseBtn.clicked.connect(self.mediaPlayer.pause)

        stopBtn = QPushButton("Stop")
        stopBtn.clicked.connect(self.mediaPlayer.stop)

        # 按钮布局
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(openBtn)
        btnLayout.addWidget(playBtn)
        btnLayout.addWidget(pauseBtn)
        btnLayout.addWidget(stopBtn)

        # 视频区布局
        videoLayout = QVBoxLayout()
        videoLayout.addWidget(self.videoWidget)
        videoLayout.addWidget(self.slider)
        videoLayout.addWidget(self.timeLabel)
        videoLayout.addWidget(self.label)
        videoLayout.addWidget(self.frame_label)
        videoLayout.addLayout(btnLayout)

        # 主布局
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.listWidget, 2)
        mainLayout.addLayout(videoLayout, 5)
        self.setLayout(mainLayout)

        # 信号连接
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.durationChanged.connect(self.update_duration)
        self.mediaPlayer.positionChanged.connect(self.update_position)
        self.mediaPlayer.mediaStatusChanged.connect(self.handle_media_status)

        self.current_index = -1

    def load_llm_res(self, path: str):

        video_path = path
        json_file = video_path.split("/")[-1].split(".")[0] + ".json"

        _path = Path(__file__).parent / "assets" / "llm_res" / json_file

        # use cv2 to get fps
        cap = cv2.VideoCapture(video_path)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        try:
            with open(_path, "r", encoding="utf-8") as f:
                self.annotations = json.load(f)
            print(f"✅ 成功加载注释：{len(self.annotations)} 条")
        except Exception as e:
            print(f"❌ 加载注释失败: {e}")
            self.annotations = []

    def find_res_with_position(self, frame_idx: int, data: dict):

        self.frame_label.setText(
            f"Current Frame: {frame_idx}, second: {frame_idx / self.fps:.2f}"
        )

        for one_info in data:

            info_frame_idx = one_info["frame_idx"]
            info_second = one_info["second"]
            info_conversation = one_info["conversation"]
            info_output_text = one_info["output_text"]

            if info_frame_idx == frame_idx:
                print(f"find res: {info_output_text}")
                break

    def get_default_videos(self):

        _path = Path(__file__).parent / "assets" / "videos"

        path_list = [str(path) for path in _path.glob("*.mp4")]

        path_list = sorted(path_list)

        self.video_paths = path_list
        self.listWidget.clear()
        for path in path_list:
            self.listWidget.addItem(path.split("/")[-1])
        self.current_index = 0
        self.load_and_play(self.current_index)

    def open_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择多个视频")
        if files:
            self.video_paths = files
            self.listWidget.clear()
            for path in files:
                self.listWidget.addItem(path.split("/")[-1])
            self.current_index = 0
            self.load_and_play(self.current_index)

    def play_selected_file(self, item):
        self.current_index = self.listWidget.row(item)
        self.load_and_play(self.current_index)

    def load_and_play(self, index):

        if 0 <= index < len(self.video_paths):
            path = self.video_paths[index]

            # FIXME: need change
            self.load_llm_res(path)

            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
            self.label.setText(f"Currently Playing:{path.split('/')[-1]}")
            self.mediaPlayer.play()


    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.play_next()

    def play_next(self):
        self.current_index += 1
        if self.current_index >= len(self.video_paths):
            self.current_index = 0  # 循环播放
        self.load_and_play(self.current_index)

    def update_duration(self, duration):
        self.slider.setMaximum(duration)
        self.update_time_label(self.mediaPlayer.position(), duration)

    def update_position(self, position):

        self.slider.setValue(position)
        self.update_time_label(position, self.mediaPlayer.duration())

        current_frame = int(position * self.fps / 1000)

        print(f"当前帧号: {current_frame}")

        self.find_res_with_position(current_frame, self.annotations)

    def update_time_label(self, current_ms, total_ms):
        current_time = QTime(0, 0, 0).addMSecs(current_ms)
        total_time = QTime(0, 0, 0).addMSecs(total_ms)
        time_str = f"{current_time.toString('mm:ss')} / {total_time.toString('mm:ss')}"
        self.timeLabel.setText(time_str)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
