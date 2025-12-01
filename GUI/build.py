# - *- encoding: utf-8 -*-
'''
use PyInstaller to build the .py file to .exe.
'''

import PyInstaller.__main__ as main

main.run([
    "GUI\\video_player_cv2_new.py",
    '--onefile',
    '--windowed',
    '--distpath=.' # compile path
])
