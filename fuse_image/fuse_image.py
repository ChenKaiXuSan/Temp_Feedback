#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
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
'''
from PIL import Image
from pathlib import Path

import itertools
import random

def random_scale_and_combine_two_images(base_image, overlay_image, direction='horizontal'):
    
    # 随机缩放图片
    scale_factor = random.uniform(0.3, 1.0)  # 缩放比例从0.3到1.0之间
    new_width = int(overlay_image.width * scale_factor)
    new_height = int(overlay_image.height * scale_factor)
    overlay_resized = overlay_image.resize((new_width, new_height), Image.ANTIALIAS)
    
    # 生成随机位置
    max_x = base_image.width - new_width
    max_y = base_image.height - new_height
    x_position = random.randint(0, max_x)
    y_position = random.randint(0, max_y)
    
    # 将缩放后的图片粘贴到基础图片上
    # FIXME: 
    base_image.paste(overlay_resized, (x_position, y_position), overlay_resized)


    return base_image

def merge_images(cold_imgs, hot_imgs, normal_imgs, output_path, direction='horizontal'):

    # 创建组合
    combinations = itertools.product(cold_imgs + hot_imgs + normal_imgs, repeat=2)

    for i, (image1_path, image2_path) in enumerate(combinations):
        
        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)

        merged_img: Image = random_scale_and_combine_two_images(image1, image2, direction)

    # 保存合并后的图片
    merged_img.save(output_path)
    print(f'图片已保存到 {output_path}')

def load_images(image_path: Path):

    cold_imgs = []
    hot_imgs = []
    normal_imgs = []

    for label in image_path.iterdir():
        if label.is_dir():
            for image in label.iterdir():
                if image.suffix in ['.jpg', '.png']:
                    if label.name == 'cold' or label.name == 'cool':
                        cold_imgs.append(image)
                    elif label.name == 'hot' or label.name == 'warm':
                        hot_imgs.append(image)
                    elif label.name == 'normal':
                        normal_imgs.append(image)
    return cold_imgs, hot_imgs, normal_imgs


if __name__ == '__main__':

    image_path = Path("/workspace/data/temp_dataset")
    output_path = Path("/workspace/data/temp_dataset/merged")

    cold_imgs, hot_imgs, normal_imgs = load_images(image_path)

    merge_images(cold_imgs, hot_imgs, normal_imgs, output_path, direction='horizontal')