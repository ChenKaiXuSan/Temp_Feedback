#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
File: /workspace/temp_feedback/Temp_Feedback/project/process.py
Project: /workspace/temp_feedback/Temp_Feedback/project
Created Date: Saturday December 2nd 2023
Author: Kaixu Chen
-----
Comment:

Have a good code time :)
-----
Last Modified: Saturday December 2nd 2023 11:37:46 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2023 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import logging
from turtle import forward 
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np 

from pytorch_lightning import LightningModule

from torchmetrics.classification import (
    MulticlassAccuracy,
    MulticlassPrecision,
    MulticlassF1Score,
    MulticlassAUROC,
    MulticlassConfusionMatrix
)

from models.make_model import make_model

class TempFeedbackLightningModule(LightningModule):

    def __init__(self, hparams):
        
        super().__init__()

        self.img_size = hparams.data.img_size  
        self.lr = hparams.optimizer.lr

        self.num_classes = hparams.model.model_class_num

        self.model = make_model(hparams)

        self.save_hyperparameters()

        self._accuracy = MulticlassAccuracy(num_classes=self.num_classes)
        self._precision = MulticlassPrecision(num_classes=self.num_classes)
        self._f1_score = MulticlassF1Score(num_classes=self.num_classes)
        self._auroc = MulticlassAUROC(num_classes=self.num_classes)
        self._confusion_matrix = MulticlassConfusionMatrix(num_classes=self.num_classes)

    def forward(self, x):
        '''
        the forward function of the model
        '''
        return self.model(x)
    
    def training_step(self, batch, batch_idx):
        '''
        the training step of the model
        '''
        x, y = batch
        logits = self.model(x)
        loss = F.cross_entropy(logits, y)
        self.log('train_loss', loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)

        accuracy = self._accuracy(logits, y)
        precision = self._precision(logits, y)
        f1_score = self._f1_score(logits, y)
        auroc = self._auroc(logits, y)
        confusion_matrix = self._confusion_matrix(logits, y)

        self.log_dict({
            'train_accuracy': accuracy,
            'train_precision': precision,
            'train_f1_score': f1_score,
            'train_auroc': auroc,
        }, on_step=True, on_epoch=True, prog_bar=True, logger=True)

        return loss

    def validation_step(self, batch, batch_idx):
        '''
        the validation step of the model
        '''
        x, y = batch
        logits = self.model(x)
        loss = F.cross_entropy(logits, y)
        self.log('val_loss', loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)

        accuracy = self._accuracy(logits, y)
        precision = self._precision(logits, y)
        f1_score = self._f1_score(logits, y)
        auroc = self._auroc(logits, y)
        confusion_matrix = self._confusion_matrix(logits, y)

        self.log_dict({
            'val_accuracy': accuracy,
            'val_precision': precision,
            'val_f1_score': f1_score,
            'val_auroc': auroc,
        }, on_step=True, on_epoch=True, prog_bar=True, logger=True)

        # return loss
    
    def test_step(self, batch, batch_idx):
        '''
        the test step of the model
        '''
        x, y = batch
        logits = self.model(x)
        loss = F.cross_entropy(logits, y)
        self.log('test_loss', loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)

        accuracy = self._accuracy(logits, y)
        precision = self._precision(logits, y)
        f1_score = self._f1_score(logits, y)
        auroc = self._auroc(logits, y)
        confusion_matrix = self._confusion_matrix(logits, y)

        self.log_dict({
            'test_accuracy': accuracy,
            'test_precision': precision,
            'test_f1_score': f1_score,
            'test_auroc': auroc,
        }, on_step=True, on_epoch=True, prog_bar=True, logger=True)

        return loss

    def configure_optimizers(self):
        '''
        the configure_optimizers of the model
        '''
        optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=3, verbose=True)
        return {
            'optimizer': optimizer,
            'lr_scheduler': scheduler,
            'monitor': 'val_loss'
        }