# How to use python crawler to get data from website

## Install Google Chrome

1. Download Google Chrome `.deb` file from web:

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
```

2. Install Google Chrome

``` bash 
sudo apt install ./google-chrome-stable_current_amd64.deb
```

3. Finish

## Virtual display  

``` bash
sudo apt-get install xvfb <- This is virtual display

sudo apt-get install screen <- This will allow you to close SSH terminal while running.

screen -S s1

Xvfb :99 -ac & DISPLAY=:99 python3 main.py
```

## Crawler in Server

We use the pyvirtualdisplay to support the crawler run in server.

The pyvirtualdisplay is a python wrapper for Xvfb, Xephyr and Xvnc.

``` bash
pip install pyvirtualdisplay
```

How to use pyvirtualdisplay:

``` python
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 600))
display.start()
# your code here
display.stop()
```

# Statement

The python crawler is used to get data from website. The data is used for research purpose only.
The source code is from [AutoCrawler](https://github.com/YoongiKim/AutoCrawler) and modified by myself.

We thank the author for his/her contribution to the open source community.

If you find this repo is useful, please star it. 😄

# Reference
1. https://zhuanlan.zhihu.com/p/137114100
2. https://github.com/YoongiKim/AutoCrawler
3. https://blog.csdn.net/freeking101/article/details/84994242
4. 