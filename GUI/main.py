from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist

from PyQt5.QtGui import *
from PyQt5.QtCore import *

# load the ui config
from UI.video_player import Ui_video_player, myVideoWidget

import sys
import os
import random
import pandas as pd
import time
from pathlib import Path

def get_video_path():
    """
    get the video path, with random shuffle, for QMediaPlayer.

    Returns:
        list: return the video path in list.
    """

    PATH = os.path.join(Path(__file__).parent, "videos")

    path_list = []
    path = os.listdir(PATH)

    for i in path:
        path_list.append(os.path.join(PATH, i))

    # random shuffle the data list
    random.shuffle(path_list)

    return path_list


def load_from_json(json_path: str):
    pass


def out_to_csv(info_dict: dict, name: str = "test"):
    """
    output the selected log in csv file, where the save path is "/logs/".

    Args:
        info_dict (dict): selected log saved as dict.
        name (str, optional): the experimenter name, used in save file. Defaults to 'test'.
    """

    info_list = []

    localtime = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

    for key in info_dict.keys():

        video_file_name = info_dict[key][0].split("\\")[1].rsplit("_", 2)[0]
        video_number = info_dict[key][0].split("\\")[1].rsplit("_", 2)[1].split("-")[1]
        flag = info_dict[key][0].split("\\")[1].rsplit("_", 1)[1].split(".")[0]

        info_dict[key].insert(0, video_file_name)
        info_dict[key].insert(1, video_number)
        info_dict[key].insert(2, flag)

        info_list.append(info_dict[key])

    df = pd.DataFrame(
        info_list,
        columns=[
            "video file name",
            "video number",
            "flag",
            "path",
            "attention",
            "disease",
        ],
        dtype=str,
    )
    df.to_csv(os.path.join("logs", "%s_%s.csv" % (name, localtime)))

    print(df)


class VideoPlayer(Ui_video_player, QMainWindow):
    """
    main window, where the right part is to play the video, and the right part to selected by experimenter.
    There are two options,
    First line: attention body part.
    Second line: disease type.

    Args:
        Ui_MainWindow (_type_): main window UI defined, store in "/UI/GUI.py"S
        QMainWindow (_type_): father class
    """

    def __init__(self):

        super(Ui_video_player, self).__init__()

        self.save_dict = {}

        self.setupUi(self)

        # get the video path
        self.path_list = get_video_path()

        self.videoFullScreen = False  # 判断当前widget是否全屏
        self.videoFullScreenWidget = myVideoWidget()  # 创建一个全屏的widget
        self.videoFullScreenWidget.setFullScreen(1)
        self.videoFullScreenWidget.hide()  # 不用的时候隐藏起来

        # put the video list into playlist.
        self.list_play_func()

        # init the btn func.
        self.signal_init()

        self.index = 1

        # display video number in textBrower
        self.textBrowser_display()

        self.name = 'teset'
        print(self.name)

    def signal_init(self):
        """
        signal init func, defined the btn function.
        """

        self.start_button.clicked.connect(
            lambda: self.btn_func(self.start_button)
        )  # play
        self.stop_button.clicked.connect(
            lambda: self.btn_func(self.stop_button)
        )  # pause
        self.next_button.clicked.connect(
            lambda: self.btn_func(self.next_button)
        )  # next

        self.videoFullScreenWidget.doubleClickedItem.connect(
            self.videoDoubleClicked
        )  # 双击响应
        self.wgt_video.doubleClickedItem.connect(self.videoDoubleClicked)  # 双击响应

    def btn_func(self, btn):
        """
        define the btn function, called by signal_init func.

        Args:
            btn (btn type): btn type, judgment conditions.
        """

        if btn == self.start_button:
            self.player.play()

        elif btn == self.stop_button:
            self.player.stop()

        elif btn == self.next_button:

            # check btn states.
            attn_total, disease_total = self.check_btn()

            if attn_total != 1:

                QMessageBox.about(self, "warning", "Focus part is single choice!")
                return

            if disease_total != 1:

                QMessageBox.about(self, "warning", "Disease is single choice!")
                return

            # when next btn clicked, fresh the btn states.
            # todo
            attn_list, disease_list = self.init_btn()

            # save selected btn info.
            self.save_info(attn_list, disease_list)

            if (
                self.playlist.currentIndex() == self.playlist.mediaCount() - 1
            ):  # if finish, finish and exit.

                QMessageBox.about(self, "attention", "finish and exit!")

                # use closeEvent(), to save selected info.
                self.close()

            else:

                # first fresh the video index
                self.playlist.setCurrentIndex(self.index)
                self.index += 1

                # then display the freshed video index
                self.textBrowser_display()

    def init_btn(self):
        """
        init the btn state, when click the next btn.
        """
        attn_list = []
        disease_list = []

        # init attention btn with multi case
        if self.head_btn.isChecked():
            self.head_btn.setChecked(False)
            attn_list.append(self.head_btn.objectName())

        if self.shoulder_btn.isChecked():
            self.shoulder_btn.setChecked(False)
            attn_list.append(self.shoulder_btn.objectName())

        if self.wrist_btn.isChecked():
            self.wrist_btn.setChecked(False)
            attn_list.append(self.wrist_btn.objectName())

        if self.lumbar_pelvis_btn.isChecked():
            self.lumbar_pelvis_btn.setChecked(False)
            attn_list.append(self.lumbar_pelvis_btn.objectName())

        if self.foot_btn.isChecked():
            self.foot_btn.setChecked(False)
            attn_list.append(self.foot_btn.objectName())

        if self.focus_unkonwn_btn.isChecked():
            self.focus_unkonwn_btn.setChecked(False)
            attn_list.append(self.focus_unkonwn_btn.objectName())

        # init disease btn
        if self.asd_btn.isChecked():
            self.asd_btn.setChecked(False)
            disease_list.append(self.asd_btn.objectName())
        elif self.non_asd_btn.isChecked():
            self.non_asd_btn.setChecked(False)
            disease_list.append(self.non_asd_btn.objectName())
        elif self.disease_unknown_btn.isChecked():
            self.disease_unknown_btn.setChecked(False)
            disease_list.append(self.disease_unknown_btn.objectName())

        return attn_list, disease_list

    def check_btn(self):
        """
        check btn states. if btn is checked, the set to False.

        Returns:
            list: the count of attn and disease, for judgment.
        """

        attn_total = 0
        disease_total = 0

        # init attention btn
        if self.head_btn.isChecked():
            attn_total += 1
        if self.wrist_btn.isChecked():
            attn_total += 1
        if self.shoulder_btn.isChecked():
            attn_total += 1
        if self.lumbar_pelvis_btn.isChecked():
            attn_total += 1
        if self.foot_btn.isChecked():
            attn_total += 1
        if self.focus_unkonwn_btn.isChecked():
            attn_total += 1

        # init disease btn
        if self.asd_btn.isChecked():
            disease_total += 1
        if self.non_asd_btn.isChecked():
            disease_total += 1
        if self.disease_unknown_btn.isChecked():
            disease_total += 1

        return attn_total, disease_total

    def textBrowser_display(self):
        """
        display the experiment state in the text browser.
        like: current number, remain, total number.
        """

        self.inforamtion.setText(
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:10pt; color:#ff0000;">current number: %s</span></p>\n'
            % str(self.playlist.currentIndex() + 1)
        )
        self.inforamtion.append(
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:10pt; color:#ff0000;">remain: %s</span></p>\n'
            % str((self.playlist.mediaCount() - self.playlist.currentIndex() - 1))
        )
        self.inforamtion.append(
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:10pt; color:#ff0000;">total number: %s</span></p>\n'
            % str(self.playlist.mediaCount())
        )

    def list_play_func(self):
        """
        first init the player and playlist.
        then add video media to the playlist, set loop video mode.
        """

        # play with playlist
        self.playlist = QMediaPlaylist(self)
        self.player = QMediaPlayer(self)
        self.player.setPlaylist(self.playlist)

        self.player.setVideoOutput(
            self.wgt_video
        )  # 视频播放输出的widget，就是上面定义的

        for path in self.path_list:
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(path)))

        self.playlist.setPlaybackMode(1)  # loop video
        self.playlist.setCurrentIndex(0)  # from 0 play

        self.player.play()

        # 当媒体加载完成后更新 slider 范围
        self.player.durationChanged.connect(self.progressBar.setMaximum)
        self.player.positionChanged.connect(self.progressBar.setValue)

    def save_info(self, attn_list: list, disease_list: list):
        """
        save the selected info to dict, called by btn func when next_btn is clicked.

        Args:
            attn_list (list): attn selected in list.
            disease_list (list): selected disease type in list.
        """

        curr_list = [
            self.path_list[self.playlist.currentIndex()],
            attn_list,
            disease_list,
        ]

        # save in global dict
        self.save_dict[self.playlist.currentIndex()] = curr_list

    def videoDoubleClicked(self):
        """
        video double clicked to full screen.
        """

        if self.player.duration() > 0:  # 开始播放后才允许进行全屏操作
            if self.videoFullScreen:
                self.player.pause()
                self.videoFullScreenWidget.hide()
                self.player.setVideoOutput(self.wgt_video)
                self.player.play()
                self.videoFullScreen = False
            else:
                self.player.pause()
                self.videoFullScreenWidget.show()
                self.player.setVideoOutput(self.videoFullScreenWidget)
                self.player.play()
                self.videoFullScreen = True

    def closeEvent(self, event) -> None:
        """
        close event, when close the window this func is called.
        In this fun, called the out_to_csv func to output the selected info (in save_dict) to the csv file.

        Args:
            event (_type_): close event.
        """

        reply = QMessageBox.question(
            self,
            "Window Close",
            "Are you sure you want to close the window?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            event.accept()
            print(self.save_dict)

            # save the selected infot with experimenter name.
            out_to_csv(self.save_dict, self.name)

        else:
            event.ignore()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    _player = VideoPlayer()
    _player.show()

    sys.exit(app.exec_())
