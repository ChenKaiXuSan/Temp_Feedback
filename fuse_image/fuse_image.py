#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: /workspace/temp_feedback/Temp_Feedback/fuse_image/fuse_image.py
Project: /workspace/temp_feedback/Temp_Feedback/fuse_image
Created Date: Monday October 7th 2024
Author: Kaixu Chen
-----
Comment:

Have a good code time :)
-----
Last Modified: Monday October 7th 2024 5:48:32 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2024 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""
from PIL import Image
from pathlib import Path
import multiprocessing

import itertools
import random
import logging


def random_scale_and_combine_two_images(back: Image, front: Image):

    # 随机缩放图片
    scale_factor = random.uniform(0.5, 1.0)  # 缩放比例从0.3到1.0之间
    if back.width > front.width and back.height > front.height:
        new_width = int(front.width * scale_factor)
        new_height = int(front.height * scale_factor)
    else:
        new_width = int(back.width * scale_factor)
        new_height = int(back.height * scale_factor)
    front_resized = front.resize((new_width, new_height), Image.ANTIALIAS)

    # 生成随机位置
    max_x = back.width - new_width
    max_y = back.height - new_height
    x_position = random.randint(0, max_x)
    y_position = random.randint(0, max_y)

    # 将缩放后的图片粘贴到基础图片上
    back.paste(front_resized, (x_position, y_position))

    return back


def find_label(img: Path):
    if "cold" in img.stem or "cool" in img.stem:
        return "cold"
    elif "hot" in img.stem or "warm" in img.stem:
        return "hot"
    else:
        return "normal"


def merge_images(first_imgs, second_imgs, output_path):

    # 创建组合
    # combinations = itertools.product(cold_imgs+hot_imgs+normal_imgs, repeat=2)
    combinations = itertools.product(first_imgs + second_imgs, repeat=2)

    for i, (image1_path, image2_path) in enumerate(combinations):

        if image1_path == image2_path:
            continue

        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)

        merged_img: Image = random_scale_and_combine_two_images(image1, image2)

        # 保存合并后的图片
        label = Path(f"back_{find_label(image1_path)}_front_{find_label(image2_path)}")

        save_path = output_path / label / f"{label}_{i}.jpg"
        if save_path.parent.exists() is False:
            save_path.parent.mkdir()

        try:
            merged_img.convert("RGB").save(save_path)
            logging.info(f"save image to: {save_path}")
        except Exception as e:
            logging.error(f"error: {e}")
            continue


def load_images(image_path: Path):

    cold_imgs = []
    hot_imgs = []
    normal_imgs = []

    for label in image_path.iterdir():
        if label.is_dir():
            for image in label.iterdir():
                if image.suffix in [".jpg", ".png"]:
                    if label.name == "cold" or label.name == "cool":
                        cold_imgs.append(image)
                    elif label.name == "hot" or label.name == "warm":
                        hot_imgs.append(image)
                    elif label.name == "normal":
                        normal_imgs.append(image)
    return cold_imgs, hot_imgs, normal_imgs


def multi_process_merge_images(cold_imgs, hot_imgs, normal_imgs, output_path):

    p1 = multiprocessing.Process(
        target=merge_images, args=(cold_imgs, hot_imgs, output_path)
    )
    p2 = multiprocessing.Process(
        target=merge_images, args=(hot_imgs, cold_imgs, output_path)
    )
    p3 = multiprocessing.Process(
        target=merge_images, args=(normal_imgs, hot_imgs, output_path)
    )

    p4 = multiprocessing.Process(
        target=merge_images, args=(hot_imgs, normal_imgs, output_path)
    )

    p5 = multiprocessing.Process(
        target=merge_images, args=(normal_imgs, cold_imgs, output_path)
    )

    p6 = multiprocessing.Process(
        target=merge_images, args=(cold_imgs, normal_imgs, output_path)
    )

    for p in [p1, p2, p3, p4, p5, p6]:
        p.start()
        p.join()        

if __name__ == "__main__":

    image_path = Path("/workspace/data/temp_dataset")
    output_path = Path("/workspace/data/temp_dataset_merged")

    if not output_path.exists():
        output_path.mkdir()

    cold_imgs, hot_imgs, normal_imgs = load_images(image_path)

    # merge_images(cold_imgs, hot_imgs, output_path)
    multi_process_merge_images(cold_imgs, hot_imgs, normal_imgs, output_path)
