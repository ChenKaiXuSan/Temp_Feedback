
<div align="center">    
 
# Video Temperature Feedback System
   
</div>
 
## Description   
This project is a video temperature feedback system. 
It is a system that can detect the temperature of a given images or videos and give feedback on the temperature. 
We try to use the deep learning method to detect the temperature of the image or video, with classification method.

## Dataset

To improve the research of the temperature feedback system, we collect a large number of images of different classes. 
For the dataset, we decide to prepare a dataset inclue 5 different classes, which are the noraml, hot, cold, warm and cool.

For the dataset, we try to use 2 different methods to collect the dataset, which are the python crawler and the DF model.

You can find the detail information about the dataset in the [dataset](./dataset_collection/README.md).

## Python crawler

You can find the pytorch crawler in the [crawler](./dataset_collection/crawler) folder.
We use the crawler to collect the dataset from the Internet, and we use the keyword to collect the dataset.
Then we annotate the dataset by human, and prepare the dataset.
You can fine the dataset prepare code in the [prepare_dataset.py](./dataset_collection/prepare_dataset.py) file.

**The keyword used to collect the dataset:**
You can find the keyword list in the [keyword.txt](./dataset_collection/crawler/keyword.yaml) file.
Here, we use 3 different languages to collect the dataset, which are English, Chinese and Japanese.

## Image Generation (Stable Diffusion)

## How to run   
First, install dependencies   
```bash
# clone project   
git clone https://github.com/YourGithubName/deep-learning-project-template

# install project   
cd deep-learning-project-template 
pip install -e .   
pip install -r requirements.txt
 ```   
 Next, navigate to any file and run it.   
 ```bash
# module folder
cd project

# run module (example: mnist as your main contribution)   
python lit_classifier_main.py    
```

## Imports
This project is setup as a package which means you can now easily import any file into any other file like so:
```python
from project.datasets.mnist import mnist
from project.lit_classifier_main import LitClassifier
from pytorch_lightning import Trainer

# model
model = LitClassifier()

# data
train, val, test = mnist()

# train
trainer = Trainer()
trainer.fit(model, train, val)

# test using the best model!
trainer.test(test_dataloaders=test)
```