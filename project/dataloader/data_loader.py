#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: /workspace/temp_feedback/Temp_Feedback/project/dataloader/data_loader.py
Project: /workspace/temp_feedback/Temp_Feedback/project/dataloader
Created Date: Thursday November 23rd 2023
Author: Kaixu Chen
-----
Comment:

Have a good code time :)
-----
Last Modified: Thursday November 23rd 2023 9:24:40 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2023 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""

# %%

from torchvision.transforms import (
    Compose,
    Lambda,
    RandomCrop,
    Resize,
    ToTensor,
    RandomHorizontalFlip,
)

from typing import Any, Callable, Dict, Optional, Type
from pytorch_lightning import LightningDataModule
import os, logging, sys, random

import torch
from torch.utils.data import DataLoader

from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader, random_split

# %%


class TempDataModule(LightningDataModule):
    def __init__(self, opt):
        super().__init__()

        self._DATA_PATH = opt.data.path
        self._TARIN_PATH = opt.train.train_path

        self._BATCH_SIZE = opt.train.batch_size
        self._NUM_WORKERS = opt.data.num_workers
        self._IMG_SIZE = opt.data.img_size

        # FIXME: here have bugs
        self.train_transform = Compose([
            Resize(size=[self._IMG_SIZE, self._IMG_SIZE]),
            ToTensor(),
            RandomCrop(size=[self._IMG_SIZE, self._IMG_SIZE]),
        ])

        self.val_transform = Compose([
            Resize(size=[self._IMG_SIZE, self._IMG_SIZE]),
            ToTensor(),
        ])

    def prepare_data(self) -> None:
        pass

    def setup(self, stage: Optional[str] = None) -> None:
        """
        assign tran, val, predict datasets for use in dataloaders

        Args:
            stage (Optional[str], optional): trainer.stage, in ('fit', 'validate', 'test', 'predict'). Defaults to None.
        """

        # if stage == "fit" or stage == None:
        if stage in ("fit", None):
            self.train_dataset = ImageFolder(
                root=os.path.join(self._DATA_PATH, "train"),
                transform=self.train_transform,
            )
            
        if stage in ("fit", "validate", None):
            self.val_dataset = ImageFolder(
                root=os.path.join(self._DATA_PATH, "val"),
                transform=self.val_transform,
            )

        if stage == "test" or stage == None:
            self.test_dataset = ImageFolder(
                root=os.path.join(self._DATA_PATH, "test"),
                transform=self.val_transform,
            )

    def train_dataloader(self) -> DataLoader:
        """
        create the Walk train partition from the list of video labels
        in directory and subdirectory. Add transform that subsamples and
        normalizes the video before applying the scale, crop and flip augmentations.
        """
        return DataLoader(
            self.train_dataset,
            batch_size=self._BATCH_SIZE,
            num_workers=self._NUM_WORKERS,
            pin_memory=True,
            shuffle=False,
            drop_last=True,
        )

    def val_dataloader(self) -> DataLoader:
        """
        create the Walk train partition from the list of video labels
        in directory and subdirectory. Add transform that subsamples and
        normalizes the video before applying the scale, crop and flip augmentations.
        """

        return DataLoader(
            self.val_dataset,
            batch_size=self._BATCH_SIZE,
            num_workers=self._NUM_WORKERS,
            pin_memory=True,
            shuffle=False,
            drop_last=True,
        )

    def test_dataloader(self) -> DataLoader:
        """
        create the Walk train partition from the list of video labels
        in directory and subdirectory. Add transform that subsamples and
        normalizes the video before applying the scale, crop and flip augmentations.
        """
        return DataLoader(
            self.test_dataset,
            batch_size=self._BATCH_SIZE,
            num_workers=self._NUM_WORKERS,
            pin_memory=True,
            shuffle=False,
            drop_last=True,
        )