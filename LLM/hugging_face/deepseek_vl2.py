#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: /workspace/code/image_to_text/deepseek.py
Project: /workspace/code/image_to_text
Created Date: Friday April 25th 2025
Author: Kaixu Chen
-----
Comment:

The deepseek api should be complied with the github repo:
https://github.com/deepseek-ai/DeepSeek-VL2

with the following command:
pip install -e .

Have a good code time :)
-----
Last Modified: Friday April 25th 2025 5:32:29 pm
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2025 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""

import logging
import json
from PIL import Image
import hydra
import omegaconf
import torch
from typing import Dict
from tqdm import tqdm
from pathlib import Path


from transformers import AutoModelForCausalLM

from deepseek_vl2.models import DeepseekVLV2Processor, DeepseekVLV2ForCausalLM

from utils.timer import timer
from utils.get_device import get_device
from utils.video_loader import split_video_and_extract_frames_decord


class DeepSeek:
    def __init__(
        self,
        output_path: str,
        prompt: dict,
        version: str = "deepseek-ai/deepseek-v12-small",
    ):

        self.device_name = get_device()
        self.output_path = Path(output_path)
        self.prompt = prompt

        self.model, self.processor = self.load_model(version)

        self.image_info = []

    @staticmethod
    def load_model(version: str):

        vl_chat_processor: DeepseekVLV2Processor = (
            DeepseekVLV2Processor.from_pretrained(version)
        )

        vl_gpt: DeepseekVLV2ForCausalLM = AutoModelForCausalLM.from_pretrained(
            version, trust_remote_code=True
        )
        vl_gpt = vl_gpt.to(torch.bfloat16).cuda().eval()

        return vl_gpt, vl_chat_processor

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

        conversation = [
            {
                "role": "<|User|>",
                "content": f"<image>\n<|ref|>{self.prompt}<|/ref|>.",
                # "images": ["./images/visual_grounding_1.jpeg"],
            },
            {"role": "<|Assistant|>", "content": ""},
        ]

        prepare_inputs = self.processor(
            conversations=conversation,
            images=[image],
            force_batchify=True,
            system_prompt="",
        ).to(self.model.device)

        inputs_embeds = self.model.prepare_inputs_embeds(**prepare_inputs)

        tokenizer = self.processor.tokenizer

        # run the model to get the response
        outputs = self.model.language.generate(
            inputs_embeds=inputs_embeds,
            attention_mask=prepare_inputs.attention_mask,
            pad_token_id=tokenizer.eos_token_id,
            bos_token_id=tokenizer.bos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            max_new_tokens=512,
            do_sample=False,
            use_cache=True,
        )

        answer = tokenizer.decode(outputs[0].cpu().tolist(), skip_special_tokens=False)

        # package the image info
        if isinstance(image_path, str):
            image_info = {
                "image_name": image_path.split("/")[-1],
                "image_path": image_path,
                "conversation": conversation,
                "output_text": answer,
            }
        elif isinstance(image_path, dict):
            image_info = {
                "video_path": video_path,
                "frame_idx": frame_idx,
                "second": second,
                "conversation": conversation,
                "output_text": answer,
            }

        self.image_info.append(image_info)

        self.save_image_info_to_json(
            self.image_info, self.output_path / "image_info.json"
        )


@hydra.main(config_path="../configs", config_name="deepseek")
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

    image_to_text = DeepSeek(
        output_path=output_path, prompt=cfg.prompt_en, version=cfg.version.model
    )

    for frame_info in tqdm(total_frame_list, desc="Processing frames"):

        image_to_text(image_path=frame_info)

    logging.info("All done!")


if __name__ == "__main__":

    load_config()
