#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
File: /workspace/temp_feedback/Temp_Feedback/project/main.py
Project: /workspace/temp_feedback/Temp_Feedback/project
Created Date: Thursday November 30th 2023
Author: Kaixu Chen
-----
Comment:

Have a good code time :)
-----
Last Modified: Thursday November 30th 2023 2:16:25 pm
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2023 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import os, logging, time, sys, random
from pytorch_lightning import Trainer, seed_everything
from pytorch_lightning import loggers as pl_loggers
from pytorch_lightning.loggers import TensorBoardLogger

# Callbacks 
from pytorch_lightning.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    LearningRateMonitor,
)

from dataloader.data_loader import TempDataModule

import hydra, torch

def train(hparams):

    seed_everything(42, workers=True)

    # init datamodule
    data_module = TempDataModule(hparams)

    # TODO: test the dataloader
    data_module.setup()
    for i in data_module.train_dataloader():
        print(i)
        break


@hydra.main(config_path="/workspace/temp_feedback/Temp_Feedback/configs", config_name="config.yaml")
def init_params(cfg):

    train(cfg)

if __name__ == "__main__":

    os.environ["CUDA_VISIBLE_DEVICES"] = "1"
    init_params()