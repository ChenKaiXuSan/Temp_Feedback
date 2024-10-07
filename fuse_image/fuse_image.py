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

def random_combine_two_images(img1, img2, direction='horizontal'):
    # 获取两张图片的大小
    width1, height1 = img1.size
    width2, height2 = img2.size

    # TODO：目前的逻辑是随机剪裁两张图片，然后合成，这里需要修改一下
    # TODO：应该是缩放一张图片之后进行合成，而不是随机剪裁
    # 随机选择合成的区域
    x1 = random.randint(0, width1 - 1)
    y1 = random.randint(0, height1 - 1)
    x2 = random.randint(0, width2 - 1)
    y2 = random.randint(0, height2 - 1)

    # 定义合成区域的大小
    box1 = (x1, y1, x1 + min(100, width1 - x1), y1 + min(100, height1 - y1))
    box2 = (x2, y2, x2 + min(100, width2 - x2), y2 + min(100, height2 - y2))

    # 裁剪两张图片
    cropped_img1 = img1.crop(box1)
    cropped_img2 = img2.crop(box2)

    # 创建一个新的空白图片
    new_img = Image.new("RGBA", (200, 200))

    # 将裁剪的部分粘贴到新图片上
    new_img.paste(cropped_img1, (0, 0))
    # TODO: 这里需要再修改一下
    new_img.paste(cropped_img2, (100, 100), cropped_img2)  # 添加 alpha 通道

    return new_img

def merge_images(cold_imgs, hot_imgs, normal_imgs, output_path, direction='horizontal'):

    # 创建组合
    combinations = itertools.product(cold_imgs + hot_imgs + normal_imgs, repeat=2)

    for i, (image1_path, image2_path) in enumerate(combinations):
        
        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)

        merged_img = random_combine_two_images(image1, image2, direction)

    # 获取每张图片的宽度和高度
    width1, height1 = image1.size
    width2, height2 = image2.size

    # 根据合并方向计算新图像的尺寸
    if direction == 'horizontal':
        # 水平合并
        new_width = width1 + width2
        new_height = max(height1, height2)
    elif direction == 'vertical':
        # 垂直合并
        new_width = max(width1, width2)
        new_height = height1 + height2
    else:
        raise ValueError("Direction must be 'horizontal' or 'vertical'")

    # 创建一个新的图像来放置两张图片
    new_image = Image.new('RGB', (new_width, new_height))

    # 将两张图片粘贴到新图像上
    new_image.paste(image1, (0, 0))
    if direction == 'horizontal':
        new_image.paste(image2, (width1, 0))
    else:
        new_image.paste(image2, (0, height1))

    # 保存合并后的图片
    new_image.save(output_path)
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