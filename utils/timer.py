#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: /Users/chenkaixu/Temp_Feedback/utils/timer.py
Project: /Users/chenkaixu/Temp_Feedback/utils
Created Date: Friday December 13th 2024
Author: Kaixu Chen
-----
Comment:
A timer decorator to calculate the running time of a function.

Have a good code time :)
-----
Last Modified: Friday December 13th 2024 10:13:47 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2024 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""
import time


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"function {func.__name__} running time: {end_time - start_time:.2f} s")
        return result

    return wrapper


# @timer
# def slow_function():
#     time.sleep(2)
#     return "Finished"


# print(slow_function())
