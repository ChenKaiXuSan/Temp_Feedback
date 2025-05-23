#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
File: /Users/chenkaixu/Temp_Feedback/tests/test_utils.py
Project: /Users/chenkaixu/Temp_Feedback/tests
Created Date: Friday December 13th 2024
Author: Kaixu Chen
-----
Comment:

Have a good code time :)
-----
Last Modified: Friday December 13th 2024 11:27:50 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2024 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import pytest
import torch

from utils.timer import timer
from utils.get_device import get_device


def test_timer():
    @timer
    def slow_function():
        assert 1 == 1
        return "Finished"

    assert slow_function() == "Finished"

def test_get_device():
    assert get_device() == "cuda" if torch.cuda.is_available() else "cpu"
    assert get_device() == "cpu" if not torch.cuda.is_available() else "cuda"
    assert get_device() == "cuda" if torch.cuda.is_available() else "cpu"
