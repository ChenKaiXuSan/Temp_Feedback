#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
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
"""

import os, logging, time, sys, random
from pytorch_lightning import Trainer, seed_everything
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    LearningRateMonitor,
)

import hydra
import torch

from project.dataloader.data_loader import TempDataModule
from project.trainer import TempFeedbackLightningModule

def train(hparams):
    seed_everything(42, workers=True)

    # init datamodule
    data_module = TempDataModule(hparams)
    temp_model = TempFeedbackLightningModule(hparams)

    # init logger
    logger = TensorBoardLogger(
        save_dir=hparams.train.log_path,
        name=hparams.model.name,
        # version=hparams.version,
    )

    # init callbacks
    lr_monitor = LearningRateMonitor(logging_interval="step")
    early_stop_callback = EarlyStopping(
        monitor="val_loss", patience=20, verbose=True, mode="min"
    )
    checkpoint_callback = ModelCheckpoint(
        monitor="val_loss",
        filename="{epoch}-{val_loss:.2f}-{val_accuracy:.2f}",
        auto_insert_metric_name=False,
        save_top_k=2,
        mode="min",
    )

    # init trainer
    trainer = Trainer(
        devices=[
            hparams.train.gpu_num,
        ],
        accelerator=get_device_name,
        max_epochs=hparams.train.max_epochs,
        logger=logger,
        check_val_every_n_epoch=1,
        callbacks=[lr_monitor, early_stop_callback, checkpoint_callback],
    )

    # start training
    trainer.fit(temp_model, data_module)

    # start testing
    trainer.test(temp_model, datamodule=data_module)


@hydra.main(
    config_path="../configs",
    config_name="config.yaml",
)
def init_params(cfg):
    # 获取设备
    train(cfg)


if __name__ == "__main__":
    # os.environ["CUDA_VISIBLE_DEVICES"] = "1"
    init_params()
