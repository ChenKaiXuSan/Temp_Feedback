#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: /workspace/temp_feedback/Temp_Feedback/utils/fuse_image/video_loader.py
Project: /workspace/temp_feedback/Temp_Feedback/utils/fuse_image
Created Date: Thursday December 19th 2024
Author: Kaixu Chen
-----
Comment:

Have a good code time :)
-----
Last Modified: Monday May 26th 2025 9:38:32 pm
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2024 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""
from decord import VideoReader, cpu
import logging
import os
import numpy as np
from pathlib import Path
from PIL import Image

logger = logging.getLogger(__name__)


def split_video_and_extract_frames_decord(video_path: Path, output_dir: Path):

    # 创建输出目录
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    total_frame_list = []

    # 使用 Decord 加载视频
    vr = VideoReader(str(video_path), ctx=cpu())
    video_fps = vr.get_avg_fps()  # 视频原始帧率
    total_frames = len(vr)  # 视频总帧数
    duration = total_frames / video_fps  # 视频时长（秒）

    print(
        f"视频帧率: {video_fps:.2f} FPS, 总帧数: {total_frames}, 时长: {duration:.2f} 秒"
    )

    current_second = 0  # 当前秒计数器
    saved_count = 0  # 记录已保存帧数

    # 遍历所有帧
    for frame_idx in range(total_frames):
        # 当前帧对应的秒
        current_second = int(frame_idx / video_fps)
        current_ms = int(frame_idx * 1000 / video_fps)

        # 提取帧并转换为 NumPy 数组
        frame = vr[frame_idx].asnumpy()
        # 转换为 PIL.Image
        image = Image.fromarray(frame)

        frame_info = {
            "video_path": video_path,
            "frame_idx": frame_idx,
            "current_ms": current_ms,
            "second": current_second,
            "image": image,
        }

        total_frame_list.append(frame_info)

        # 保存帧到输出目录
        output_path = os.path.join(
            output_dir, f"frame_{frame_idx}_second_{current_second}_ms_{current_ms}.jpg"
        )
        image.save(output_path)
        print(f"保存帧: {output_path}")
        saved_count += 1

    print(f"视频分割和帧提取完成，共保存 {saved_count} 帧！")

    return total_frame_list
