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
import hydra
import omegaconf
import torch
from typing import Dict
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from pathlib import Path

from utils.timer import timer
from utils.get_device import get_device

# 配置日志输出到文件
# TODO: log 输出的位置需要修改一下
logging.basicConfig(
    filename='app.log',           # 输出的日志文件名
    level=logging.INFO,           # 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S'   # 日期时间格式
)

class Qwen2VL:
    def __init__(self, output_path: str, prompt: dict):

        self.device_name = get_device()
        self.output_path = Path(output_path)
        self.prompt = prompt

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

        with torch.inference_mode():
            # Inference: Generation of the output
            output_ids = self.model.generate(**inputs, max_new_tokens=512)
            generated_ids = [
                output_ids[len(input_ids) :]
                for input_ids, output_ids in zip(inputs.input_ids, output_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
            )
            logging.info(output_text)

        return output_text
    
    def save_image_info_to_json(self, image_info: dict, json_file_path: Path):
        
        full_path = json_file_path

        if full_path.exists() is False:
            full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w") as f:
            json.dump(image_info, f, indent=4)

    def __call__(self, image_path: Path, text: str = "Describe this image."):

        image = Image.open(image_path).convert("RGB")
        logging.info(image.size)

        whole_output_text = {}

        for idx, text in self.prompt.items():
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

            whole_output_text[idx] = self.generate(inputs)        
        
        # package the image info
        # TODO: 这里的组装方式还可以修改一下
        image_info = {
            "image_name": image_path.stem,
            "image_path": str(image_path),
            "conversation": conversation,
            "output_text": whole_output_text,
        }

        self.image_info.append(image_info)

        self.save_image_info_to_json(self.image_info, self.output_path / "image_info.json")
            
@hydra.main(config_path="../configs", config_name="gpt_prompts")
def load_config(cfg: omegaconf.DictConfig):
    
    output_path = cfg.output_path

    # test image path
    images_path = [Path("tests/data/sample.jpg"), Path("tests/data/fire.jpg")]

    image_to_text = Qwen2VL(output_path=output_path, prompt=cfg.prompt)

    for image_path in images_path:
        image_to_text(image_path)
    
    
if __name__ == "__main__":

    load_config()