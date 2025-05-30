<div align="center">

# GUI for Image-Text Model Prediction Result

</div>

## Description

This project make the GUI for displaying the image-text model's prediction result.

Detailed comments are written for most of the functions and classes.
Have a happy code. 😄

## Folder structure

```bash
.
|-- README.md # This file
|-- arduino_r4
|   `-- test.ino
|-- arduino_serial.py
|-- assets
|   |-- llm_res
|       |-- test1\ copy.json
|       `-- test1.json
|-- build.py
|-- main.py
|-- requirements.txt
|-- video_player_cv2.py
`-- video_player_qmedia_player.py
```

## How to run

1. first should put the video file and the annotations file in the ./assets/videos and ./assets/llm_res/ directory.

   The video file should be in the format of `.mp4` or `.avi`, and the annotations file should be in the format of `.json`.

   We provide a sample video file, where can be download from YouTube, and the annotations file is in the `assets/llm_res` directory.

   ```bash
   # make sure you are in the root directory of the project
   python utils\youtube_dl.py
   ```
   This will download a sample video file and save it in the `assets/videos` directory.

2. Install the required libraries.

   We use OpenCV and PyQt5 to build the GUI.

   Make sure you install the PyQt5 and OpenCV libraries before running the code.
   You can install them with the following commands:

   ```bash
   pip install PyQt5
   pip install opencv-python
   ```

   or you can install all the requirements in [requirements.txt](requirements.txt):

3. Run the `video_player_cv2.py` file to start the GUI application.

   ```bash
   # make sure you are in the root directory of the project
   python GUI/video_player_cv2.py
   ```

## PyInstaller

In [build.py](build.py), can use PyInstaller to compile the .py file to .exe app.
For the final user.

> ⚠️ Users should first check the **manual.docx** document to see how to use this application.
