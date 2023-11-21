
<div align="center">    
 
# Video Temperature Feedback System
   
</div>
 
## Description   
This project is a video temperature feedback system. 
It is a system that can detect the temperature of a given images or videos and give feedback on the temperature. 
We try to use the deep learning method to detect the temperature of the image or video, with classification method.

## Dataset

To improve the research of the temperature feedback system, we collect a large number of images and videos of different session. 
For the dataset, we decide to prepare a dataset inclue three different session, which are the normal session (N), the high session (H) and the cold session (C).
To detail the different temperature of the session, we split hot/cold session into different level, which are high (H1), medium (H2), low (H3) and cold (C1), medium (C2), low (C3).

The class in the dataset is as follows:
1. c1，c2，c3
2. h1，h2，h3
3. n

About the Hot flag, we think the image should include fire.

List 

- 温暖：春天，沙滩，阳光，蓝天白云
- 炎热：夏天，沙漠，火焰，热带雨林，沙漠，太阳，火山
- 凉爽：秋天，瀑布，大海，河流，湖泊，森林，树木，草地，草原，枫叶，月亮（？）
- 寒冷：冬天，雪地，雪花，雪球，滑雪，羽绒服，冰灯，南极，溜冰场
- 一般：室内，草坪

5个类别，一个类别收集2k张图片，1.5k用来训练，0.5k用来测试。
使用5Fold CV。

> trick：使用三种不同的语言来进行搜索，英文，中文，日文。
可以增加图片的数量。


## The keyword used to collect the dataset:
sun	晴
sunshine	阳光
rain	雨
snow	雪
hail	冰雹
drizzle	毛毛雨
sleet	冰雨
shower	阵雨
mist	薄雾
fog	雾
cloud	云
rainbow	彩虹
wind	大风
breeze	微风
strong winds	强风
thunder	打雷
lightning	闪电
storm	暴风
thunderstorm	雷暴
gale	大风
tornado	旋风
hurricane	飓风
flood	洪水
frost	霜
ice	冰
drought	干旱
heat wave	暖流
windy	有风
cloudy	多云
foggy	有雾
misty	薄雾
icy	结冰
frosty	霜冻
stormy	有雷雨
dry	干燥
wet	有雨水
hot	热
cold	冷
chilly	寒
sunny	晴朗
rainy	下雨
fine	晴天
dull	阴天
overcast	多云
humid	湿润


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