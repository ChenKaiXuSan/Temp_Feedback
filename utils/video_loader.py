#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
File: /workspace/temp_feedback/Temp_Feedback/utils/fuse_image/video_loader.py
Project: /workspace/temp_feedback/Temp_Feedback/utils/fuse_image
Created Date: Thursday December 19th 2024
Author: Kaixu Chen
-----
Comment:

Have a good code time :)
-----
Last Modified: Thursday December 19th 2024 12:00:47 pm
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2024 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''
from decord import VideoReader, cpu, gpu
import os
import numpy as np
from PIL import Image

def split_video_and_extract_frames_decord(video_path: str, output_dir: str, fps=2):
    """
    使用 Decord 按秒分割视频并从每秒中抽取指定数量帧。
    
    :param video_path: 视频文件路径
    :param output_dir: 输出帧的保存目录
    :param fps: 每秒提取的帧数
    """

    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    total_frame_list = []

    # 使用 Decord 加载视频
    vr = VideoReader(video_path, ctx=cpu())
    video_fps = vr.get_avg_fps()  # 视频原始帧率
    total_frames = len(vr)  # 视频总帧数
    duration = total_frames / video_fps  # 视频时长（秒）
    
    print(f"视频帧率: {video_fps:.2f} FPS, 总帧数: {total_frames}, 时长: {duration:.2f} 秒")

    # 每秒需要抽取的帧的间隔（在当前秒的帧范围内均匀分布）
    frame_interval = int(video_fps / fps)
    
    current_second = 0  # 当前秒计数器
    saved_count = 0  # 记录已保存帧数

    # 遍历所有帧
    for frame_idx in range(total_frames):
        # 当前帧对应的秒
        current_second = int(frame_idx / video_fps)

        # 检查是否在当前秒范围内按照间隔抽取帧
        if (frame_idx % frame_interval == 0) and (frame_idx // video_fps == current_second):
            # 提取帧并转换为 NumPy 数组
            frame = vr[frame_idx].asnumpy()
            # 转换为 PIL.Image
            image = Image.fromarray(frame)
            
            frame_info = {
                "video_path": video_path,
                "frame_idx": frame_idx,
                "second": current_second,
                "image": image
            }

            total_frame_list.append(frame_info)

            # 保存帧到输出目录
            output_path = os.path.join(output_dir, f"second_{current_second}_frame_{frame_idx}.jpg")
            image.save(output_path)
            print(f"保存帧: {output_path}")
            saved_count += 1
    
    print(f"视频分割和帧提取完成，共保存 {saved_count} 帧！")

    return total_frame_list