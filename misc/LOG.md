# Workflow 

1. Collect images from the Internet, meanwhile try to use the DF model to generate images.
2. Label the images by human, and prepare the dataset.
3. make the code of the system.
    1. make the dataloaer.
    2. make the model with different CV model.
    3. make the loss function.
4. Train the model.
5. Test the model.


# log

## 2023-12-3

之前写好了数据集的划分代码，放在
```
./dataset_collection/prepare_dataset.py
```
里面，并且把准备好的数据集放在
```
./data/splited_dataset
```
里面。
其中，`./data`数据集里面包含所有的训练使用数据。
```
./data
├── download # raw data from python crawler
├── splited_dataset # splited dataset, in train/val/test, splited by 7:2:1
└── temp_dataset # a temp dataset, help merge the whole class from download
```

整体数据集准备的处理流程如下：

``` mermaid
graph LR
    pytorch_crawler --> A[download] --> B(temp_dataset)
    B --> C(splited_dataset)
```

**但是，训练之后的结果并不好。**

val loss很大，并且val acc很低，只有0.14左右。
train loss 和 train acc都很高，但是val loss很高，说明模型过拟合了。

具体原因还在分析中，不知。

之后尝试使用了PCA降维，但是效果并不好，因为没有经过分类器的缘故，出来的图片特征都集中在一起。

我们数据集的PCA分布如下：
![pca](../dataset_collection/analyse/pca.png)

为了确定是否正确，我使用同样的方法对cifar10进行了PCA，结果如下：
![pca](../dataset_collection/analyse/cifar10_pca.png)

可以看到是没有什么区别的，猜测的原因是因为我们的数据没有经过分类器，所以效果不好。

~~PS: 找时间写一下数据的分布图。~~
17:40:34：
已解决，观察数据分布发现存在数据不均衡的问题，所以在数据集划分的时候，需要注意数据的均衡性。
结果在`./dataset_collection/analyse/data_distributed.ipynb`下。

## 2020-12-6

和学姐商量的结果，决定先从爬到的数据中，选出一部分数据（进行人工筛选），然后进行训练，看看效果如何。
目前这个工作交给了nakamura，也不知道什么时候可以做完。
我是不是应该先自己准备一些数据进行测试呢。

## 2020-12-7

果然还是应该自己先选一些数据集进行测试，nakamura的作业速度太慢了。

## 2023-12-10

有一篇论文，是关于训练数据集应该准备多少图像才比较合适的。
https://pdf.sciencedirectassets.com/273474/1-s2.0-S1574954120X00021/1-s2.0-S1574954120300352/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEH0aCXVzLWVhc3QtMSJIMEYCIQCZqBC%2BKKDGuPkIH4iGEyVk%2Bg4pTCOWqSWS25XrHGvenAIhAPIiT7gQuuSSgyPQvX3sVvy6LEBH7Uh5URC1EDpc8VgFKrwFCOX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQBRoMMDU5MDAzNTQ2ODY1Igz7TTZq4o%2FBElnKYzEqkAW6GbRkeqpCKWKCApzv71e%2BcKEz%2BwGqmdSOwLjRS4Thq1kSU%2B%2BORu%2B2RzENX9cQBMu9fXViX%2BrcLo2Y2tIQkf%2F2CfIXMD%2F7Jq9pzfJ%2Fp60ySQ0%2BEFKuGmJKWHAoZxDE2v8F9pB9XJUH2q5Pkw1FCjhQjUvnUICQKZNwsGEuxBkM7JJyyDRJQZ5ujtbNABAvy%2FQ32t6VafwPRpZt%2FHzOm5zt9c19zLZa14JfzB4j0sFhhpp9rIzTE6NwXQEiHSwaJUme8MmFBaAwoN0uq%2FTESE6tnXCRpBLu1EpmNc8DdhC4rl%2BNUL9PZXg4cardqyTbFWnYZx2zs7mL4AwwF%2BYFGxg5OvsqGmtFx1ghxzwMsMDMrqbRlc9j63j4I7fmoh7D59lK6tNq%2BSlbGUUdnpPvG2a4n6ofaWxDitjgZjSG5rC4Xq7s86cvB42bir0BdsvcSLIv7pFq41difBs0i32Oe%2BbfohX3SCmCcMN0n49xcD0%2BGD3iq3LUkJ%2Bq1ylho%2FNrnGjzBdfuF6FLfPv8emGQvDut%2BWXJsWo0REy%2Ff%2FeVikr5laUy4HXxsfIRJiPLnANzNMRZZBtlLWyslkLvxzCWNQZQnk92c1JJMnDhSuQoqcMSyhUU1eTvj%2FtgkkoMEEMybxGChIGUeoARFDFrGnziq2KaE%2FrV3nFCZd9b7wA0OAJAJPkXE%2BAq5US2PJBxnby2vcBKua8hWontLklSGHyAnEXj8Ibxfly14yJwFrvGMOT84vtec%2B%2FoPnf1ItGVptGsQeJaMotuqaA252cfsIXV3KC3pt5EFZZAm%2FKXXp%2Fin8RTybtjE2GCEUHYCESlZ4kVVNzyVyGAGsvzaIfLM8qLVDDnZviMo6uBo3xPQsSnvFEbRTC69dSrBjqwAVpBa%2BKIPbQ%2BYWJgsFJdyRdNyj94trpL8udbei7Kd5xDwngWZC9t%2FuTsFFT2YeF7VlaLJmnHSwLYM01umoPGs9hoYNiYDYZWX%2B5NELMeG4e8R4Eol3FUSo7fimBuiTBLvr8MMPWNaTPrKVSd43irwuczciZo6bdk4SG5irJfhoFZxECFniDBw%2FxUEX06lhBJILoqHL7RHmz7EqamUAe8KDd4zNa2%2FfjQD9sB6eQsVXRV&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20231210T045858Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTY3YAD7EV6%2F20231210%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=ba09b750f6aef831971bb6460c080337af1fee2f43df99911b36e73cb5db68b3&hash=d24f1aa2958a29c454a131b02bd9555c77af6c9099f5b37dc97375dc121b7e93&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S1574954120300352&tid=spdf-67cccba0-bb6a-472c-ba19-818eddb9d33f&sid=207ac59d6ecf8646c3096b1180d1e224749agxrqa&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=08135d525553030f54&rr=8332ea756edc2636&cc=jp

也许可以参考一下这篇论文，然后计算一下多少数据比较合适。
需要做对比实验，并且提供详细的比较曲线。

## 2023-12-22

下周和国内研究室的老师开个会，需要提前准备一下slide。
实验方面，先自己做几个小的数据集，对比一下效果。
主要还是数据平衡的问题，比较需要解决。

## 2024-10-7

通过讨论之后，准备先把不同的图片分为全局和局部。
然后随机融合全局和局部的图片来进行测试。