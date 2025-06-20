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
import json
import hydra
import omegaconf
import torch
import shutil
from pathlib import Path
from tqdm import tqdm

from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from transformers import Qwen2_5_VLForConditionalGeneration

from utils.timer import timer
from utils.get_device import get_device
from utils.video_loader import split_video_and_extract_frames_decord

logger = logging.getLogger(__name__)


def save_image_info_to_json(image_info: dict, json_file_path: Path):

    # save_image_info = {
    #     "video_path": str(image_info["video_path"]),
    #     "frame_idx": int(image_info["frame_idx"]),
    #     "second": int(image_info["second"]),
    #     "ms": int(image_info["ms"]),
    #     "conversation": image_info["conversation"],
    #     "output_text": image_info["output_text"],
    # }

    if json_file_path.parent.exists() is False:
        json_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(json_file_path, "w") as f:
        json.dump(image_info, f, indent=4)


class Qwen2VL:
    def __init__(
        self,
        output_path: str,
        prompt: dict,
        version: str = "Qwen/Qwen2.5-VL-7B-Instruct",
        cache_dir: str = "",
    ):

        self.device_name = get_device()
        self.output_path = Path(output_path)
        self.prompt = prompt

        self.model, self.processor = self.load_model(
            version, self.device_name, cache_dir
        )

    @staticmethod
    def load_model(version: str, device_name: str, cache_dir: str = ""):

        if not Path(cache_dir).exists():
            logger.info(f"Creating cache directory at {cache_dir}")
            Path(cache_dir).mkdir(parents=True, exist_ok=True)

        if "Qwen2.5" in version:
            model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                version, torch_dtype="auto", cache_dir=cache_dir
            ).to(device_name)
        elif "Qwen2" in version:
            model = Qwen2VLForConditionalGeneration.from_pretrained(
                version, torch_dtype="auto", cache_dir=cache_dir
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

    def get_conversation(self, role: str, content: dict):
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
            # logger.info(output_text)

        return output_text

    def __call__(self, frame_info: dict):

        video_path = frame_info["video_path"]
        frame_idx = frame_info["frame_idx"]
        current_ms = frame_info["current_ms"]
        second = frame_info["second"]
        image = frame_info["image"]

        logger.info(
            f"Processing frame {frame_idx} at {video_path} - second: {second}, ms: {current_ms}"
        )

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

        # package the image info
        image_info = {
            "video_path": str(video_path),
            "frame_idx": int(frame_idx),
            "second": int(second),
            "ms": int(current_ms),
            "conversation": conversation,
            "output_text": self.generate(inputs),
        }

        # logger.info(f"Saving image info to JSON at {_output_path / 'image_info.json'}")
        save_image_info_to_json(
            image_info,
            self.output_path
            / f"frame_{frame_idx}_second_{second}_ms_{current_ms}.json",
        )

        return image_info


@hydra.main(config_path="../../configs", config_name="qwen2")
def load_config(cfg: omegaconf.DictConfig):

    output_path = Path(cfg.output_path)
    video_path = Path(cfg.video_path)
    assets_path = Path(cfg.assets_path)

    for pth in tqdm(video_path.iterdir(), desc="video file"):

        res_imgae_info = []

        _output_path = output_path / pth.stem

        total_frame_list = split_video_and_extract_frames_decord(
            pth, _output_path / "frames"
        )

        image_to_text = Qwen2VL(
            output_path=_output_path / "image_info",
            prompt=cfg.prompt_en,
            version=cfg.version.model,
            cache_dir=cfg.cache_path,
        )

        for frame_info in tqdm(total_frame_list, desc="Processing frames"):

            _img_info = image_to_text(frame_info=frame_info)
            res_imgae_info.append(_img_info)

        # Save the results to a JSON file
        logger.info(f"Results saved to {_output_path / f'{_output_path.stem}.json'}")

        save_image_info_to_json(
            res_imgae_info,
            _output_path / f"{_output_path.stem}.json",
        )

        # copy the video file to the assets path 
        if not (_output_path).exists():
            _output_path.mkdir(parents=True, exist_ok=True)
        
        shutil.copy(_output_path / f"{_output_path.stem}.json", f"{assets_path / _output_path.stem}.json")

        logger.info(f"Processed video: {pth.stem}")

        # Clean up        
        del image_to_text
        del res_imgae_info
        torch.cuda.empty_cache()

    logger.info("All done!")


if __name__ == "__main__":

    load_config()
