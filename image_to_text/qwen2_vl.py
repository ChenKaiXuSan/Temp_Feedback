#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
File: /Users/chenkaixu/Temp_Feedback/image_to_text/qwen2-vl.py
Project: /Users/chenkaixu/Temp_Feedback/image_to_text
Created Date: Saturday December 14th 2024
Author: Kaixu Chen
-----
Comment:
https://huggingface.co/Qwen/Qwen2-VL-7B-Instruct

Have a good code time :)
-----
Last Modified: Sunday December 15th 2024 7:14:46 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2024 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import logging
import os 
import json
from PIL import Image
import torch
from typing import Dict
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from pathlib import Path

from utils.timer import timer
from utils.get_device import get_device

class Qwen2VL:
    def __init__(self, output_path: Path):

        self.device_name = get_device()
        self.output_path = output_path

        self.load_model()
        self.image_info = []
    
    def load_model(self):

        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            "Qwen/Qwen2-VL-7B-Instruct", torch_dtype="auto"
        ).to(self.device_name)

        self.min_pixels = 256 * 28 * 28
        self.max_pexels = 1280 * 28 * 28

        self.processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct", min_pixels=self.min_pixels, max_pixels=self.max_pexels)

    def get_conversation(self, role: str, content: Dict):
        conversation = [
            {
                "role": role,
                "content": content
            }
        ]
        return conversation

    def preprocess(self, converstaion, image, device_name):
        # Preprocess the inputs
        text_prompt = self.processor.apply_chat_template(converstaion, add_generation_prompt=True)
        # Excepted output: '<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n<|vision_start|><|image_pad|><|vision_end|>Describe this image.<|im_end|>\n<|im_start|>assistant\n'

        inputs = self.processor(
            text=[text_prompt], images=[image], padding=True, return_tensors="pt"
        )
        inputs = inputs.to(device_name)

        return inputs

    @timer
    def generate(self, inputs):

        # Inference: Generation of the output
        output_ids = self.model.generate(**inputs, max_new_tokens=512)
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(inputs.input_ids, output_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )
        print(output_text)

        return output_text
    
    def save_image_info_to_json(self, image_info: dict, json_file_path: Path):
        
        full_path = Path(os.getcwd()) / json_file_path

        if full_path.exists() is False:
            full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w") as f:
            json.dump(image_info, f, indent=4)

    def __call__(self, image_path: Path, text: str = "Describe this image."):

        image = Image.open(str(Path(os.getcwd()) / image_path)).convert("RGB")
        print(image.size)

        conversation = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                    },
                    {"type": "text", "text": text},
                ],
            }
        ]

        inputs = self.preprocess(conversation, image, self.device_name)

        output_text = self.generate(inputs)        
        
        # package the image info
        image_info = {
            "image_name": image_path.stem,
            "image_path": str(image_path),
            "conversation": conversation,
            "output_text": output_text,
        }

        self.image_info.append(image_info)

        self.save_image_info_to_json(self.image_info, self.output_path / "image_info.json")
            


if __name__ == "__main__":

    output_path = Path("logs/qwen2-vl_result")

    # test image path
    images_path = [Path("tests/data/sample.jpg"), Path("tests/data/fire.jpg")]
    
    text: str = "Describe the tempurature of the figure."
    image_to_text = Qwen2VL(output_path=output_path)


    for image_path in images_path:
        image_to_text(image_path, text)
    