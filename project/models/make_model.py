#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: /workspace/temp_feedback/Temp_Feedback/project/models/make_model.py
Project: /workspace/temp_feedback/Temp_Feedback/project/models
Created Date: Thursday November 23rd 2023
Author: Kaixu Chen
-----
Comment:

Have a good code time :)
-----
Last Modified: Thursday November 23rd 2023 9:21:31 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2023 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""


# %%
# from pytorchvideo.models import x3d, resnet, csn, slowfast, r2plus1d

from os import name
from typing import Any
import torch
import torch.nn as nn
from torchvision.models import resnet50, ResNet50_Weights

from torchvision.models import (
    resnet18,
    ResNet18_Weights,
    resnet50,
    ResNet50_Weights,
    resnet101,
    ResNet101_Weights,
    resnet152,
    ResNet152_Weights,
    alexnet,
    AlexNet_Weights,
    densenet121,
    DenseNet121_Weights,
    densenet161,
    DenseNet161_Weights,
    densenet169,
    DenseNet169_Weights,
    densenet201,
    DenseNet201_Weights,
    squeezenet1_0,
    SqueezeNet1_0_Weights,
    squeezenet1_1,
    SqueezeNet1_1_Weights,
    vgg11,
    VGG11_Weights,
    vgg13,
    VGG13_Weights,
    vgg16,
    VGG16_Weights,
    vgg19,
    VGG19_Weights,
    mobilenet_v3_small,
    MobileNet_V3_Small_Weights,
    mobilenet_v3_large,
    MobileNet_V3_Large_Weights,
)


class MakeTempModule(nn.Module):
    def __init__(self, hparams) -> None:
        super().__init__()

        self.model_class_num = hparams.model.model_class_num
        self.model_depth = hparams.model.model_depth
        self.model_name = hparams.model.name
        self.transfor_learning = hparams.train.transfor_learning

    def make_resnet(self, depth: int = 50, input_channel: int = 3) -> nn.Module:
        if self.transfor_learning:
            if depth == 18:
                network = resnet18(weights=ResNet18_Weights)
            elif depth == 50:
                network = resnet50(weights=ResNet50_Weights)
            elif depth == 101:
                network = resnet101(weights=ResNet101_Weights)
            elif depth == 152:
                network = resnet152(weights=ResNet152_Weights)
            else:
                raise ValueError("The model name is not in the choice.")

            # change the output to model class num
            network.fc = nn.Linear(network.fc.in_features, self.model_class_num)

        else:
            network = resnet50()

            network.fc = nn.Linear(network.fc.in_features, self.model_class_num)

        return network

    def forward(self, name, depth, input_channel):
        if name == "resnet":
            return self.make_resnet(depth, input_channel)
        else:
            raise ValueError("The model name is not in the choice.")


def make_model(hparams):
    """a helper function to make the model by the hparams.model.name.

    Args:
        hparams (hydra): hpamras, include the model name, model class num, model depth, and so on.

    Raises:
        ValueError: when the model name is not in the choice, raise the error.

    Returns:
        nn.Module: the model
    """

    name = hparams.model.name
    depth = hparams.model.model_depth
    input_channel = hparams.model.model_class_num

    model = MakeTempModule(hparams)

    return model(name, depth, input_channel)
