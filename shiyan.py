import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# 随机生成最高次为3的多项式系数（这里包含0次项，所以是4个系数）
np.random.seed(0)  # 为了复现结果设置随机种子
coefficients = np.random.uniform(-10, 10, 4)


# 创建一个函数来生成多项式的值
def polynomial(x, coefficients):
    """计算形如 a + bx + cx^2 + dx^3 的多项式的值"""
    y = sum(coef * x ** i for i, coef in enumerate(coefficients))
    return y


# 生成数据
x_values = np.linspace(-10, 10, 100)
y_values = polynomial(x_values, coefficients)

# 转换成PyTorch张量
X_train = torch.tensor(x_values, dtype=torch.float32).view(-1, 1)
Y_train = torch.tensor(y_values, dtype=torch.float32).view(-1, 1)


# 定义一个模型
class PolynomialRegressionModel(nn.Module):
    def __init__(self):
        super(PolynomialRegressionModel, self).__init__()
        # 定义一个多项式模型，输入和输出大小都是1，但内部会有多个参数
        self.poly = nn.Linear(4, 1)

    def forward(self, x):
        # 生成多项式的次数，x的0次方，1次方，2次方，3次方
        poly_features = torch.cat((x ** 0, x ** 1, x ** 2, x ** 3), dim=1)
        return self.poly(poly_features)


# 创建模型
model = PolynomialRegressionModel()

# 定义损失函数和优化器
criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

# 训练模型
epochs = 1000
for epoch in range(epochs):
    # 前向传播
    Y_pred = model(X_train)

    # 计算损失
    loss = criterion(Y_pred, Y_train)

    # 反向传播和优化
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # 打印训练信息
    if epoch % 100 == 0:
        print(f'Epoch {epoch + 1}/{epochs}, Loss: {loss.item():.4f}')

# 输出训练后的模型参数
params = model.poly.weight.data.numpy()[0]
print(f"Trained polynomial coefficients: {params}")
