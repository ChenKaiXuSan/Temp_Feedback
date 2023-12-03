import numpy as np
from sklearn.decomposition import PCA
from sklearn.datasets import fetch_openml
import matplotlib.pyplot as plt

# 加载CIFAR-10数据集
cifar_10 = fetch_openml(name='CIFAR_10')
X = np.array(cifar_10.data.astype('float32'))
y = np.array(cifar_10.target.astype('int'))

# 数据预处理和标准化
X_mean = np.mean(X, axis=0)
X_std = np.std(X, axis=0)
X_normalized = (X - X_mean) / X_std

# 计算协方差矩阵
cov_matrix = np.cov(X_normalized, rowvar=False)

# 计算特征向量和特征值
eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

# 选择主成分数量
total_variance = np.sum(eigenvalues)
explained_variance_ratio = eigenvalues / total_variance
cumulative_explained_variance_ratio = np.cumsum(explained_variance_ratio)

# 选择保留总方差的百分比（例如，90%）
target_variance_ratio = 0.9
num_components = np.argmax(cumulative_explained_variance_ratio >= target_variance_ratio) + 1

# 使用PCA进行降维
pca = PCA(n_components=num_components)
X_pca = pca.fit_transform(X_normalized)

# 可视化降维后的数据
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap='viridis', alpha=0.5)
plt.title('PCA of CIFAR-10 dataset')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.savefig('cifar10_pca.png')
plt.show()
