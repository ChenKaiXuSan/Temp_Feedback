#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
File: /workspace/temp_feedback/Temp_Feedback/tests/decomplicate.py
Project: /workspace/temp_feedback/Temp_Feedback/tests
Created Date: Saturday December 2nd 2023
Author: Kaixu Chen
-----
Comment:
This script is used to test the decomposition of the dataset.
The movitation is to find the reason why the model can not learn the dataset, 
aka the model can not fit in the val/test datsset.

In this script, we use PCA to decompose the dataset, and visualize the dataset.
PCA from the sklearn package is used.

Have a good code time :)
-----
Last Modified: Saturday December 2nd 2023 4:21:38 pm
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2023 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''
import numpy
import torch
import torchvision.transforms as transforms
from torchvision import datasets
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# 定义数据转换
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)), transforms.CenterCrop(224)])

# load the dataset 
train_dataset = datasets.ImageFolder(root='/workspace/data/splited_dataset/train', transform=transform)
test_dataset = datasets.ImageFolder(root='/workspace/data/splited_dataset/test', transform=transform)

# 提取图像数据并将其转换为 PyTorch 张量
train_data = torch.stack([train_dataset[i][0].reshape(-1) for i in range(len(train_dataset))], dim=0)
train_targets = torch.cat([torch.tensor([train_dataset[i][1]]) for i in range(len(train_dataset))], dim=0)

test_data = torch.stack([test_dataset[i][0].reshape(-1) for i in range(len(test_dataset))], dim=0)
test_targets = torch.cat([torch.tensor([test_dataset[i][1]]) for i in range(len(test_dataset))], dim=0)

# # 使用PCA进行降维
n_components = 2  # 选择主成分的数量，这里选择2维便于可视化
pca = PCA(n_components=n_components)
data_pca = pca.fit_transform(train_data, train_targets)

# 可视化降维后的数据
plt.scatter(data_pca[:, 0], data_pca[:, 1], c=train_targets, cmap='viridis')
plt.title('PCA Visualization of Image Dataset')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.colorbar(label='Class')
plt.savefig('pca.png')
plt.show()
