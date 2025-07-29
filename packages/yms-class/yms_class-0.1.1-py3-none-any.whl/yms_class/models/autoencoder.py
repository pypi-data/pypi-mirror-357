import os

import torch
from PIL import Image
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


from yms_class.src.efficient_kan import KAN


class CustomDataset(Dataset):
    def __init__(self, root_dir, transform=None, class_to_label=None):
        self.root_dir = root_dir
        self.transform = transform or transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.class_to_label = class_to_label if class_to_label is not None else {}
        self.images = [f for f in os.listdir(root_dir) if f.endswith(('.bmp', '.jpg', '.png'))]

        # 如果没有提供class_to_label字典，我们在这里创建它
        if not self.class_to_label:
            self._create_class_to_label_mapping()
            self.idx_to_labels = {i: cls_name for i, cls_name in enumerate(self.class_to_label)}

    def _create_class_to_label_mapping(self):
        # 假设类别是从0开始编号的连续整数
        self.classes = sorted(set([filename.split('_')[0] for filename in self.images]))
        self.class_to_label = {cls: i for i, cls in enumerate(self.classes)}

    def get_class_to_label(self):
        return self.class_to_label

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        # 获取图片路径
        image_path = os.path.join(self.root_dir, self.images[idx])
        # 打开图片并转换为RGB格式
        # image = Image.open(image_path).convert('RGB')
        image = Image.open(image_path)
        # 如果有变换，则进行变换
        if self.transform:
            image = self.transform(image).view(-1)

        # 提取文件名中的类别
        base_filename = os.path.splitext(self.images[idx])[0]
        class_name = base_filename.split('_')[0]
        # 将类别转换为标签
        label = self.class_to_label[class_name]

        return image, label

def create_dataloader(data_path, batch_size, transform=None, num_workers=0, train_shuffle=True):
    # 训练集数据加载器
    train_dir = os.path.join(data_path, 'train')
    train_dataset = CustomDataset(root_dir=train_dir, transform=transform)
    # 初始化验证集Dataset
    validation_dir = os.path.join(data_path, 'val')  # 替换为你的验证集图片目录
    validation_dataset = CustomDataset(root_dir=validation_dir, transform=transform)
    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=train_shuffle,
                                  num_workers=num_workers)
    val_loader = DataLoader(dataset=validation_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader

class AutoencoderClassifier(nn.Module):
    def __init__(self, input_dim=30000, latent_dim=512, num_classes=4):
        super(AutoencoderClassifier, self).__init__()

        # 分类器部分
        self.classifier = nn.Sequential(
            # nn.Linear(1024, 512),
            # nn.BatchNorm1d(512),
            # nn.ReLU(),
            # nn.Dropout(0.3),
            #
            # nn.Linear(512, 256),
            # nn.BatchNorm1d(256),
            # nn.ReLU(),
            #
            nn.Linear(input_dim, 16384),
            nn.BatchNorm1d(16384),
            nn.ReLU(),
            nn.Dropout(0.5),

            nn.Linear(16384, 8192),
            nn.BatchNorm1d(8192),
            nn.ReLU(),
            nn.Dropout(0.5),

            nn.Linear(8192, 4096),
            nn.BatchNorm1d(4096),
            nn.ReLU(),
            nn.Dropout(0.5),

            # nn.Linear(4096, 2048),
            # nn.BatchNorm1d(2048),
            # nn.ReLU(),
            # nn.Dropout(0.5),

            KAN([4096, 2048, 1024, 512, 256, 128, 4]),
            # nn.ReLU(),
            # nn.Linear(128, num_classes)
        )

    def forward(self, x):
        # 分类
        logits = self.classifier(x)

        return logits


class Autoencoder(nn.Module):
    def __init__(self, input_dim=30000):
        super(Autoencoder, self).__init__()

        # 分类器部分
        self.encoder = nn.Sequential(
            # nn.Linear(input_dim, 16384),
            # nn.BatchNorm1d(16384),
            # nn.ReLU(),
            # nn.Dropout(0.5),

            nn.Linear(input_dim, 8192),
            nn.BatchNorm1d(8192),
            nn.ReLU(),
            nn.Dropout(0.5),
            #
            # nn.Linear(8192, 4096),
            # nn.BatchNorm1d(4096),
            # nn.ReLU(),
            # nn.Dropout(0.5),

            nn.Linear(8192, 4096),
        )
        # 解码器部分（对称结构）
        self.decoder = nn.Sequential(
            nn.Linear(4096, 8192),
            nn.BatchNorm1d(8192),
            nn.ReLU(),
            nn.Dropout(0.5),

            # nn.Linear(4096, 8192),
            # nn.BatchNorm1d(8192),
            # nn.ReLU(),
            # nn.Dropout(0.5),

            # nn.Linear(8192, 16384),
            # nn.BatchNorm1d(16384),
            # nn.ReLU(),
            # nn.Dropout(0.5),

            nn.Linear(8192, input_dim),
            # 最后一层不加激活函数，使用MSE损失直接优化
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded


class ResidualBlock(nn.Module):
    def __init__(self, input_dim, hidden_dim, dropout=0.2):
        """
        残差块结构
        :param input_dim: 输入特征维度
        :param hidden_dim: 隐藏层维度
        :param dropout: Dropout概率
        """
        super().__init__()
        # 主路径
        self.block = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, input_dim)
        )

        # 跳跃连接 (仅在维度不匹配时启用)
        self.shortcut = nn.Identity()
        if input_dim != hidden_dim:
            self.shortcut = nn.Linear(input_dim, hidden_dim)

        # 正则化组件
        self.layer_norm = nn.LayerNorm(input_dim)
        self.activation = nn.ReLU(inplace=True)

    def forward(self, x):
        identity = x  # 保留原始输入

        # 主路径
        out = self.block(x)

        # 残差连接
        if identity.shape[-1] == out.shape[-1]:
            out += identity
        else:
            out += self.shortcut(identity)

        # 层归一化 + 激活
        out = self.layer_norm(out)
        return self.activation(out)


class PureFCResNet(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_dim=256, num_blocks=4, dropout=0.2):
        """
        纯全连接残差网络
        :param input_dim: 输入特征维度
        :param output_dim: 输出维度
        :param hidden_dim: 隐藏层维度 (默认256)
        :param num_blocks: 残差块数量 (默认4)
        :param dropout: Dropout概率 (默认0.2)
        """
        super().__init__()
        # 输入层
        self.input_layer = nn.Sequential(
            # nn.Linear(input_dim, 16384),
            # nn.BatchNorm1d(16384),
            # nn.ReLU(),
            # nn.Dropout(0.5),

            # nn.Linear(16384, 8192),
            # nn.BatchNorm1d(8192),
            # nn.ReLU(),
            # nn.Dropout(0.5),

            nn.Linear(input_dim, 4096),
            nn.BatchNorm1d(4096),
            nn.ReLU(),
            nn.Dropout(0.5),

            nn.Linear(4096, 2048),
            nn.BatchNorm1d(2048),
            nn.ReLU(),

            # nn.Linear(input_dim, hidden_dim),
            # nn.ReLU(inplace=True)
        )

        # 残差块堆叠
        self.res_blocks = nn.Sequential()
        for i in range(num_blocks):
            self.res_blocks.add_module(
                f"res_block_{i}",
                ResidualBlock(2048, 2048, dropout)
            )

        # 输出层
        # self.output_layer = nn.Linear(hidden_dim, output_dim)
        self.output_layer = KAN([2048, 1024, 512, 256, 128, 4])

    def forward(self, x):
        # 初始变换
        x = self.input_layer(x)
        # 通过残差块
        x = self.res_blocks(x)
        # 输出结果
        return self.output_layer(x)
