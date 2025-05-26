#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
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
Last Modified: Friday December 13th 2024 9:07:04 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2024 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""

from PIL import Image, ImageDraw
from transformers import BlipProcessor, BlipForConditionalGeneration

from pathlib import Path
import json
import logging
import time
from typing_extensions import deprecated

from utils.get_device import get_device
from utils.timer import timer


def load_images(image_path: Path):
    """load images from the image_path.

    Args:
        image_path (Path): path to the image.

    Returns:
        list: list of image paths.
    """    
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

    def __init__(self, output_path: Path, device: str):
        super().__init__()

        self.device = device
        self.load_model(device)

        self.output_path = output_path
        self.image_info = []

    def load_model(self, device: str):

        self.processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-large"
        )
        self.model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-large"
        ).to(device)

    @deprecated("instead of using this method, use image2text_con and image2text_uncon")
    def image_to_text(self, image_path: Path, text: str = "a photography of"):

        image = Image.open(image_path).convert("RGB")

        # conditional image captioning
        start_time = time.time()
        inputs = self.processor(image, text, return_tensors="pt").to(self.device)

        con_out = self.model.generate(**inputs)
        logging.info(self.processor.decode(con_out[0], skip_special_tokens=True))
        forward_time = time.time() - start_time
        logging.info(f"con forward time: {forward_time}")

        # unconditional image captioning
        start_time = time.time()
        inputs = self.processor(image, return_tensors="pt").to(self.device)

        uncon_out = self.model.generate(**inputs)
        logging.info(self.processor.decode(uncon_out[0], skip_special_tokens=True))
        forward_time = time.time() - start_time
        logging.info(f"uncon forward time: {forward_time}")

        return self.processor.decode(
            con_out[0], skip_special_tokens=True
        ), self.processor.decode(uncon_out[0], skip_special_tokens=True)

    @timer
    def image2text_con(self, image_path: Path, text: str = "a photography of"):
        """convert image to text using conditional image captioning.

        Args:
            image_path (Path): path to the image.
            text (str, optional): the text used for conditional. Defaults to "a photography of".

        Returns:
            str: text generated from the image.
        """        

        image = Image.open(image_path).convert("RGB")
        print(image.size)
        # conditional image captioning
        inputs = self.processor(image, text, return_tensors="pt").to(self.device)

        con_out = self.model.generate(**inputs)

        return self.processor.decode(con_out[0], skip_special_tokens=True)

    @timer
    def image2text_uncon(self, image_path: Path):
        """convert image to text using unconditional image captioning.

        Args:
            image_path (Path): path to the image.

        Returns:
            str: text generated from the image.
        """        

        image = Image.open(image_path).convert("RGB")
        print(image.size)

        # unconditional image captioning
        inputs = self.processor(image, return_tensors="pt").to(self.device)

        uncon_out = self.model.generate(**inputs)

        return self.processor.decode(uncon_out[0], skip_special_tokens=True)

    @deprecated("not used")
    def add_text_to_image(
        self,
        image_path,
        text,
        output_path: Path,
        position=(0, 0),
        color=(255, 255, 255),
    ):
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

        if image.mode != "RGB":
            image = image.convert("RGB")

        image.save(output_path)

    def save_image_info_to_json(self, image_info: dict, json_file_path: Path):
        """save image info into json file.

        Args:
            image_info (dict): image info in dict format.
            json_file_path (Path): path to save the json file.
        """        

        # Ensure the directory for the JSON file exists.
        if json_file_path.exists() is False:
            json_file_path.parent.mkdir(parents=True, exist_ok=True)

        # save image info into json file.
        with open(json_file_path, "w", encoding="utf-8") as file:
            json.dump(image_info, file, ensure_ascii=False, indent=4)

    def __call__(self, image_path: Path):

        # con_out, uncon_out = self.image_to_text(image_path)
        con_out = self.image2text_con(image_path)
        uncon_out = self.image2text_uncon(image_path)

        # package the image info
        image_info = {
            "image_name": image_path.stem,
            "image_path": str(image_path),
            "con_text": con_out,
            "uncon_text": uncon_out,
        }

        self.image_info.append(image_info)

        self.save_image_info_to_json(
            image_info=self.image_info,
            json_file_path=self.output_path / "image_info.json",
        )


if __name__ == "__main__":

    device = get_device()

    output_path = Path("logs/blip_result")

    if device.type == "cuda":
        logging.info("Using GPU")

        image_path = Path("/workspace/data/temp_dataset")

        test_images = load_images(image_path)

    elif device.type == "cpu" or device.type == "mps":
        logging.info("Using CPU")

        test_images = [Path("tests/data/sample.jpg"), Path("tests/data/fire.jpg")]

    # Initialize the ImageToText class
    image_to_text = ImageToText(output_path, device)

    for img_path in test_images:

        image_to_text(img_path)
