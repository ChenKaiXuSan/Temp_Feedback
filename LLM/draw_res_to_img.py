#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: /Users/chenkaixu/Temp_Feedback/image_to_text/qwen2-vl.py
Project: /Users/chenkaixu/Temp_Feedback/image_to_text
Created Date: Saturday December 14th 2024
Author: Kaixu Chen
-----
Comment:
https://huggingface.co/Qwen/

The Qwen series can use the huggingface processor.

Have a good code time :)
-----
Last Modified: Friday April 25th 2025 6:22:26 pm
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2024 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""

import logging
import json
from pathlib import Path
from tqdm import tqdm
import re
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np

logger = logging.getLogger(__name__)


def convert_str_dict(llm_res):
    match = re.search(r"\{.*?\}", llm_res[0], re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return {"source": "none", "proportion": "none", "location": "none"}


def draw_text_with_font(
    frame, text_lines, positions, font_path, font_size=40, font_color=(255, 255, 255)
):
    """
    在图像上用指定字体绘制多行文字。

    Args:
        frame (np.ndarray): 原始 OpenCV 图像 (BGR)。
        text_lines (List[str]): 要绘制的多行文字。
        positions (List[Tuple[int, int]]): 每行文字的位置。
        font_path (str): 字体文件路径（.ttf/.ttc）。
        font_size (int): 字体大小。
        font_color (Tuple[int, int, int]): 文字颜色 (RGB)。

    Returns:
        np.ndarray: 绘制完文字后的图像（BGR）。
    """

    # 转换 BGR 到 RGB，并转为 PIL 图像
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(frame_rgb)
    draw = ImageDraw.Draw(image_pil)

    # 加载字体
    font = ImageFont.truetype(font_path, font_size)

    # 绘制每一行文字
    for text, pos in zip(text_lines, positions):
        draw.text(pos, text, font=font, fill=font_color)

    # 转回 OpenCV 格式（BGR）
    return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

def extract_sort_key(file_path):
    # 提取文件名中的数字：frame_0_second_0_ms_123.jpg → [0, 0, 123]
    numbers = list(map(int, re.findall(r'\d+', file_path.name)))
    return numbers  # 例如：[0, 0, 123]

def merge_res_to_img(info_path: Path, output_path: Path):

    for video in tqdm(info_path.iterdir(), desc="video file"):

        logger.info(f"Processed video: {video.stem}")

        _frames = video / "frames"
        _image_info = video / "image_info"

        overlay_res = []

        # 排序两个文件夹中所有文件
        frames_sorted = sorted(_frames.iterdir(), key=extract_sort_key)
        info_sorted = sorted(_image_info.iterdir(), key=extract_sort_key)

        for f, res in tqdm(
            zip(frames_sorted, info_sorted),
            desc="frame and image_info",
            total=len(list(_frames.iterdir())),
        ):

            # load frame
            frame = cv2.imread(f)
            frame_height, frame_width = frame.shape[:2]

            overlay = frame.copy()

            # load image info
            with open(res, "r") as f_info:
                image_info = json.load(f_info)

            _info_dict = convert_str_dict(image_info["output_text"])

            if _info_dict:
                source = _info_dict["source"].upper()
                proportion = _info_dict["proportion"] * 100
                location = _info_dict["location"]

                line_spacing = 90  # 每行文字的垂直间距（可根据字体大小调整）
                num_lines = 2

                # FIXME: the position is err some times, need to be fixed
                # 动态计算每一行的位置（从下往上）
                positions = [
                    (20, frame_height - line_spacing * (num_lines - i))  # 例如：(20, 580), (20, 650)
                    for i in range(num_lines)
                ]

                overlay = draw_text_with_font(
                    overlay,
                    [
                        f"TYPE: {source}",
                        f"PROPORTION: {proportion}%",
                    ],
                    positions,
                    font_path="/workspace/code/LLM/TIMESBD.TTF",
                    font_size=80,
                    font_color=(255, 255, 255),
                )

            overlay_res.append(overlay)

        # 定义视频编码器和输出路径
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 编码格式
        _opt_path = output_path / "video_text_vis"
        _opt_path.mkdir(parents=True, exist_ok=True)

        out = cv2.VideoWriter(
            f"{_opt_path}/{video.stem}_text.mp4",
            fourcc,
            30.0,
            (frame_width, frame_height),
        )

        for f in tqdm(overlay_res, desc="write video"):
            # 将处理后的帧写入视频
            out.write(f)

        out.release()

        logger.info(f"Video saved: {_opt_path}/{video.stem}_text.mp4")

    logger.info("All done!")


if __name__ == "__main__":

    info_path = Path(
        "/workspace/code/logs/qwen2-vl_result/Qwen/Qwen2.5-VL-7B-Instruct/2025-06-19/20-59-38"
    )
    output_path = Path("logs")

    merge_res_to_img(
        info_path=info_path,
        output_path=output_path,
    )
