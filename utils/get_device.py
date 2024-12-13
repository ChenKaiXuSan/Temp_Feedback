#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: /Users/chenkaixu/Temp_Feedback/project/utils/get_device.py
Project: /Users/chenkaixu/Temp_Feedback/project/utils
Created Date: Friday December 13th 2024
Author: Kaixu Chen
-----
Comment:

Have a good code time :)
-----
Last Modified: Friday December 13th 2024 9:06:59 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2024 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""

import torch

def get_device():
    """get device

    Returns:
        str: device name
    """
    if torch.cuda.is_available():  # 优先检查 CUDA
        local_device = torch.device("cuda")
        print(f"used device: {local_device} ({torch.cuda.get_device_name(0)})")
    elif (
        torch.backends.mps.is_available() and torch.backends.mps.is_built()
    ):  # 检查 MPS
        local_device = torch.device("mps")
        print("used device: MPS (Metal Performance Shaders)")
    else:  # 默认使用 CPU
        local_device = torch.device("cpu")
        print("used device: CPU")
    return local_device