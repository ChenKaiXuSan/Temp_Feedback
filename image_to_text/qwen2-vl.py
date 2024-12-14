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
Last Modified: Saturday December 14th 2024 11:16:40 pm
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2024 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from PIL import Image
import requests
import torch
from torchvision import io
from typing import Dict
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor

from utils.get_device import get_device


if __name__ == "__main__":
    device_name = get_device()

    # Load the model in half-precision on the available device(s)
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen2-VL-7B-Instruct", torch_dtype="auto"
    ).to(device_name)

    processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct")

    # Image
    url = "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"
    image = Image.open(requests.get(url, stream=True).raw)

    conversation = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                },
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ]


    # Preprocess the inputs
    text_prompt = processor.apply_chat_template(conversation, add_generation_prompt=True)
    # Excepted output: '<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n<|vision_start|><|image_pad|><|vision_end|>Describe this image.<|im_end|>\n<|im_start|>assistant\n'

    inputs = processor(
        text=[text_prompt], images=[image], padding=True, return_tensors="pt"
    )
    inputs = inputs.to(device_name)

    # Inference: Generation of the output
    output_ids = model.generate(**inputs, max_new_tokens=128)
    generated_ids = [
        output_ids[len(input_ids) :]
        for input_ids, output_ids in zip(inputs.input_ids, output_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
    )
    print(output_text)
