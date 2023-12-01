#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: /workspace/temp_feedback/Temp_Feedback/dataset_collection/prepare_dataset.py
Project: /workspace/temp_feedback/Temp_Feedback/dataset_collection
Created Date: Thursday November 30th 2023
Author: Kaixu Chen
-----
Comment:

Have a good code time :)
-----
Last Modified: Thursday November 30th 2023 8:13:43 am
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2023 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

30-11-2023	Kaixu Chen	finish the prepare_dataset.py
the flow chart is:
raw_dataset_path(download) -> save_dataset_path(temp_data) -> splited_dataset_path(splitted_dataset)
# TODO: the splitted_dataset_path should be changed to temp_dataset, means the splitted datast do not need to be saved.
"""

import os, shutil, sys, random
from pathlib import Path
import argparse
from sklearn.model_selection import train_test_split


CLASS = ("cold", "cool", "warm", "hot", "normal")
FLAG = ("train", "val", "test")


def count_number_dataset(save_dataset_path: Path):
    """count the number of the dataset
    the save_dataset_path structure should be:
    dataset path/class/img.jpg

    Args:
        save_dataset_path (Path): the path of the dataset
    """
    ans = {}
    for class_name in save_dataset_path.iterdir():
        if class_name.is_dir():
            ans[class_name.name] = len(list(class_name.iterdir()))

    print(ans)


def get_parameters():
    """get parameters from command line

    Returns:
        parser: inclue the parameters
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--raw_dataset_path",
        type=str,
        default="/workspace/data/download",
        help="Raw dataset path",
    )
    parser.add_argument(
        "--save_dataset_path",
        type=str,
        default="/workspace/data/temp_dataset",
        help="Save dataset path",
    )

    return parser.parse_known_args()


def make_dataset(raw_dataset_path: Path, save_dataset_path: Path):
    """move the dataset from raw_dataset_path to save_dataset_path
    mean while rename the image name

    Args:
        raw_dataset_path (Path): raw dataset path
        save_dataset_path (Path): save dataset path
    """    

    if not save_dataset_path.exists():
        save_dataset_path.mkdir(parents=True)

    for class_name in raw_dataset_path.iterdir():
        if class_name.is_dir() and class_name.name.split("_")[1] in CLASS:
            # print(class_name.name)

            if not (save_dataset_path / class_name.name.split("_")[1]).exists():
                (save_dataset_path / class_name.name.split("_")[1]).mkdir(parents=True)

            for key_word in class_name.iterdir():
                if key_word.is_dir():
                    for i, image in enumerate(sorted(key_word.iterdir())):
                        if image.is_file():
                            # make the new file name
                            img_list = image.name.split("_")
                            img_list[-1] = "{:0>4d}".format(i) + ".jpg"
                            shutil.copy(
                                image,
                                save_dataset_path
                                / class_name.name.split("_")[1]
                                / "_".join(img_list),
                            )


def split_dataset(
    save_dataset_path: Path, train_ratio: float, val_ratio: float, test_ratio: float
):
    """split the dataset into train, val, test
    the dataset structure is:
    dataset
    ├── train
    │   ├── class1
    │   ├── class2
    │   ├── class3
    │   ├── class4
    │   └── class5
    ├── val
    │   ├── class1
    │   ├── class2
    │   ├── class3
    │   ├── class4
    │   └── class5
    └── test
        ├── class1
        ├── class2
        ├── class3
        ├── class4
        └── class5

    Args:
        save_dataset_path (Path): the path of the dataset
        train_ratio (float): the ratio of the train dataset
        val_ratio (float): the ratio of the val dataset
        test_ratio (float): the ratio of the test dataset
    """

    SPLITED_DATA_PATH = Path("/workspace/data/splited_dataset")

    # check the ratio
    if round(train_ratio + val_ratio + test_ratio) != 1.0:
        print("The sum of the ratio is not 1")
        sys.exit(1)

    # check the dataset if exist
    if not SPLITED_DATA_PATH.exists():
        SPLITED_DATA_PATH.mkdir(parents=True)
        print("The dataset is not exist, make the dataset folder")
    elif SPLITED_DATA_PATH.exists():
        print("The dataset is exist, delete the dataset folder")
        shutil.rmtree(SPLITED_DATA_PATH)
        print("And make the dataset folder")
        SPLITED_DATA_PATH.mkdir(parents=True)

    # make the dataset folder
    for t in FLAG:
        if not (SPLITED_DATA_PATH / t).exists():
            for c in CLASS:
                (SPLITED_DATA_PATH / t / c).mkdir(parents=True)

    for class_name in save_dataset_path.iterdir():
        if class_name.is_dir():
            # get the image list
            image_list = list(class_name.iterdir())
            random.shuffle(image_list)

            # split the dataset
            train_num = int(len(image_list) * train_ratio)
            val_num = int(len(image_list) * val_ratio)
            test_num = int(len(image_list) * test_ratio)

            # copy the image to the train dataset
            for image in image_list[:train_num]:
                shutil.copy(
                    image,
                    SPLITED_DATA_PATH / "train" / class_name.name / image.name,
                )

            # copy the image to the val dataset
            for image in image_list[train_num : train_num + val_num]:
                shutil.copy(
                    image,
                    SPLITED_DATA_PATH / "val" / class_name.name / image.name,
                )

            # copy the image to the test dataset
            for image in image_list[train_num + val_num :]:
                shutil.copy(
                    image,
                    SPLITED_DATA_PATH / "test" / class_name.name / image.name,
                )
    print("Split the dataset successfully")


if __name__ == "__main__":
    parames, unknown = get_parameters()

    raw_dataset_path = Path(parames.raw_dataset_path)
    save_dataset_path = Path(parames.save_dataset_path)

    # Step1: make the dataset, from raw_dataset_path to save_dataset_path
    make_dataset(raw_dataset_path, save_dataset_path)

    # Step2: check the dataset
    # count image number of save_dataset_path
    count_number_dataset(save_dataset_path)

    # Step3: split the dataset into train, val, test
    # train:val:test = 7:2:1
    split_dataset(save_dataset_path, 0.7, 0.2, 0.1)

    # Step4: check the splitted dataset
    for f in FLAG:
        print(f)
        count_number_dataset(Path(f"/workspace/data/splited_dataset/{f}"))
