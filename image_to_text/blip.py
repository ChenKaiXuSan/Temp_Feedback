#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
File: /workspace/temp_feedback/Temp_Feedback/image_to_text/blip.py
Project: /workspace/temp_feedback/Temp_Feedback/image_to_text
Created Date: Wednesday December 11th 2024
Author: Kaixu Chen
-----
Comment:
A scrip to convert image to text using Blip model.
https://huggingface.co/Salesforce/blip-image-captioning-large

Have a good code time :)
-----
Last Modified: Wednesday December 11th 2024 10:44:01 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2024 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from PIL import Image, ImageDraw
from transformers import BlipProcessor, BlipForConditionalGeneration

from pathlib import Path
import os
import json
import logging
import multiprocessing
import itertools
import random
import time 

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

class ImageToText:

    def __init__(self, output_path: Path):
        super().__init__()
        self.load_model()

        self.output_path = output_path
        self.image_info = []

    def load_model(self):

        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to("cuda")

    def image_to_text(self, image_path: Path):

        image = Image.open(image_path).convert('RGB')

        # conditional image captioning
        start_time = time.time()
        text = "a photography of"
        inputs = self.processor(image, text, return_tensors="pt").to("cuda")

        con_out = self.model.generate(**inputs)
        print(self.processor.decode(con_out[0], skip_special_tokens=True))
        forward_time = time.time() - start_time
        print(f"con forward time: {forward_time}")

        # unconditional image captioning
        start_time = time.time()
        inputs = self.processor(image, return_tensors="pt").to("cuda")

        uncon_out = self.model.generate(**inputs)
        print(self.processor.decode(uncon_out[0], skip_special_tokens=True))
        forward_time = time.time() - start_time
        print(f"uncon forward time: {forward_time}")

        return self.processor.decode(con_out[0], skip_special_tokens=True), self.processor.decode(uncon_out[0], skip_special_tokens=True)

    def add_text_to_image(self, image_path, text, output_path: Path, position=(0, 0), color=(255, 255, 255)):
        """
        Adds text to an image and saves the result.

        :param image_path: Path to the input image.
        :param text: Text to add to the image.
        :param output_path: Path to save the output image.
        :param position: Tuple (x, y) for the text position.
        :param font_path: Path to the .ttf font file. Defaults to a basic PIL font if None.
        :param font_size: Size of the font.
        :param color: Color of the text in RGB format.
        """

        # Open the image
        image = Image.open(image_path)

        # Initialize the drawing context
        draw = ImageDraw.Draw(image)

        # Add text to image
        draw.text(position, text, fill=color)

        # Save the edited image
        if output_path.exists() is False:
            output_path.parent.mkdir(parents=True, exist_ok=True)

        if image.mode != 'RGB':
            image = image.convert('RGB')

        image.save(output_path)

    def save_image_info_to_json(self, image_info: dict, json_file_path: Path):
        """
        Saves the image path and associated text to a JSON file.

        :param image_path: Path to the image file.
        :param text: Text associated with the image.
        :param json_file_path: Path to the JSON file where data will be saved.
        """

        # Ensure the directory for the JSON file exists
        if json_file_path.exists() is False:
            json_file_path.parent.mkdir(parents=True, exist_ok=True)

        # 将更新后的列表写回 JSON 文件
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(image_info, file, ensure_ascii=False, indent=4)

    def __call__(self, image_path: Path):

        con_out, uncon_out = self.image_to_text(image_path)


        # self.add_text_to_image(
        #     image_path=image_path,
        #     text=con_out,
        #     output_path=self.output_path / f"{image_path.stem}.jpg",
        #     position=(50, 50),
        #     color=(255, 255, 255) 
        # )

        image_info = {
            "image_name": image_path.stem,
            "image_path": str(image_path),
            "con_text": con_out,
            "uncon_text": uncon_out
        }

        self.image_info.append(image_info)

        self.save_image_info_to_json(
            image_info=self.image_info,
            json_file_path=self.output_path / f"image_info.json"
        )


if __name__ == '__main__':

    image_path = Path("/workspace/data/temp_dataset")
    output_path = Path("logs/blip_result")

    cold_imgs, hot_imgs, normal_imgs = load_images(image_path)

    image_to_text = ImageToText(output_path)

    test_image = [Path("/workspace/temp_feedback/Temp_Feedback/tests/data/sample.jpg")]

    for img_path in test_image:

        image_to_text(img_path)

