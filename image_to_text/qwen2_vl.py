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
import os
import json
from PIL import Image
import hydra
import omegaconf
import torch
from pathlib import Path
from typing import Dict
from tqdm import tqdm

from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from transformers import Qwen2_5_VLForConditionalGeneration

from utils.timer import timer
from utils.get_device import get_device
from utils.video_loader import split_video_and_extract_frames_decord


class Qwen2VL:
    def __init__(
        self,
        output_path: str,
        prompt: dict,
        version: str = "Qwen/Qwen2.5-VL-7B-Instruct",
    ):

        self.device_name = get_device()
        self.output_path = Path(output_path)
        self.prompt = prompt

        self.model, self.processor = self.load_model(version, self.device_name)
        self.image_info = []

    @staticmethod
    def load_model(version: str, device_name: str):

        if "Qwen2.5" in version:
            model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                version, torch_dtype="auto"
            ).to(device_name)
        elif "Qwen2" in version:
            model = Qwen2VLForConditionalGeneration.from_pretrained(
                version, torch_dtype="auto"
            ).to(device_name)
        else:
            raise ValueError(
                f"Unsupported model version: {version}. Please use Qwen2 or Qwen2.5."
            )

        min_pixels = 256 * 28 * 28
        max_pexels = 1280 * 28 * 28

        processor = AutoProcessor.from_pretrained(
            version,
            min_pixels=min_pixels,
            max_pixels=max_pexels,
        )

        return model, processor

    def get_conversation(self, role: str, content: Dict):
        conversation = [{"role": role, "content": content}]
        return conversation

    def preprocess(self, converstaion, image, device_name):
        # Preprocess the inputs
        text_prompt = self.processor.apply_chat_template(
            converstaion, add_generation_prompt=True
        )
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
            output_ids = self.model.generate(**inputs, max_new_tokens=2048)
            generated_ids = [
                output_ids[len(input_ids) :]
                for input_ids, output_ids in zip(inputs.input_ids, output_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            logging.info(output_text)

        return output_text

    def save_image_info_to_json(self, image_info: dict, json_file_path: Path):

        full_path = json_file_path

        if full_path.parent.exists() is False:
            full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w") as f:
            json.dump(image_info, f, indent=4)

    def __call__(self, image_path: Path, text: str = "Describe this image."):

        if isinstance(image_path, str):
            image = Image.open(image_path).convert("RGB")
            logging.info(image.size)
        elif isinstance(image_path, dict):
            video_path = image_path["video_path"]
            frame_idx = image_path["frame_idx"]
            second = image_path["second"]
            image = image_path["image"]

        whole_output_text = {}

        if isinstance(self.prompt, str):
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                        },
                        {"type": "text", "text": self.prompt},
                    ],
                }
            ]
        else:
            # TODO: 这里的逻辑还可以修改一下
            conversation = self.get_conversation("user", self.prompt)

        inputs = self.preprocess(conversation, image, self.device_name)

        whole_output_text[0] = self.generate(inputs)

        # package the image info
        # TODO: 这里的组装方式还可以修改一下
        if isinstance(image_path, str):
            image_info = {
                "image_name": image_path.split("/")[-1],
                "image_path": image_path,
                "conversation": conversation,
                "output_text": whole_output_text,
            }
        elif isinstance(image_path, dict):
            image_info = {
                "video_path": video_path,
                "frame_idx": frame_idx,
                "second": second,
                "conversation": conversation,
                "output_text": whole_output_text,
            }

        self.image_info.append(image_info)

        self.save_image_info_to_json(
            self.image_info, self.output_path / "image_info.json"
        )


@hydra.main(config_path="../configs", config_name="qwen2")
def load_config(cfg: omegaconf.DictConfig):

    output_path = cfg.output_path

    # test image path
    # images_path = [Path("tests/data/sample.jpg"), Path("tests/data/fire.jpg")]
    # for image_path in images_path:
    #     image_to_text(image_path)

    video_path = "tests/data/downloaded_video.mp4"

    total_frame_list = split_video_and_extract_frames_decord(
        video_path, output_path + "/frames", fps=2
    )

    image_to_text = Qwen2VL(
        output_path=output_path, prompt=cfg.prompt_en, version=cfg.version.model
    )

    for frame_info in tqdm(total_frame_list, desc="Processing frames"):

        image_to_text(image_path=frame_info)

    logging.info("All done!")


if __name__ == "__main__":

    load_config()
