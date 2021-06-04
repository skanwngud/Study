import torch
import torch.nn as nn
import torch.nn.functional as F
import datetime

from torchvision import datasets, transforms

str_time = datetime.datetime.now()

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'current device is {device}')

train_data = datasets.CIFAR10(
    root='data',
    train=True,
    download=False,
    transform=transforms.Compose([
        transforms.ToTensor(),
        transforms.RandomHorizontalFlip(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
)

test_data = datasets.CIFAR10(
    root='data',
    train=False,
    download=False,
    transform=transforms.Compose([
        transforms.ToTensor(),
        transforms.RandomHorizontalFlip(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
)

train_loader = torch.utils.data.DataLoader(
    train_data, batch_size = 32
)

test_loader = torch.utils.data.DataLoader(
    test_data, batch_size = 32
)

# Resnet modeling
class BasicBlock(nn.Module):                                    # 내부에서 반복 되는 block 으로 구성 (block 먼저 정의한 후 이를 바탕으로 구현 예정)
    def __init__(self, in_planes, planes, stride = 1):          # BasicBlock 의 인스턴스를 생성할 때 지니게 되는 성질
        super(BasicBlock, self).__init__()                      # nn.Module 내에 있는 메서드를 상속 받아 이용

        self.conv1 = nn.Conv2d(                                 # 이미지 특성 추출을 위한 convolution layer 정의
            in_planes,                                          # 인스턴스 생성할 때 정의하는 in_planes 를 input channel 로 정의
            planes,                                             # 인스턴스를 생성할 때 정의하는 planes 를 output channel 로 정의
            kernel_size=3,                                      # nn.Conv2d 에서 사용 할 filter 의 크기를 정의
            stride = stride,                                    # filter 가 움직이는 범위
            padding = 1,                                        # 이미지의 끝단은 중심보다 연산량이 떨어지기 때문에 해당 최외측에 인근한 1칸의 범위를 0 으로 채움
            bias = False,                                       # convolution 연산을 진행한 후에 bias 를 추가로 더해줄지에 대한 옵션
        )
        self.bn1 = nn.BatchNorm2d(planes)                       # 각 layer 마다 input 의 분포가 달라짐에 따라 학습 속도가 느려지는 것을 방지하며 과적합 방지
        self.conv2 = nn.Conv2d(                                 # self.bn1 값을 통과한 이미지 특성을 받음, input 은 위 레이어의 output 이므로 같은 모양
            planes, 
            planes,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=False,
        )
        self.bn2 = nn.BatchNorm2d(planes)

        self.shortcut = nn.Sequential()                         # 기존의 값과 convolution 및 BatchNormalization 한 결과를 더함
        if stride != 1 or in_planes != planes:                  # stride 가 1 이 아니거나, in_planes 가 planes 와 같지 않다면, 즉 두번 째 블록부터 적용 되는 shortcut 을 정의함
            self.shortcut = nn.Sequential(
                nn.Conv2d(                                      # 기존 conv 레이어들과 같은 방식으로 레이어를 정의
                    in_planes,
                    planes,
                    kernel_size=1,                              # filter 의 크기는 1 이므로 kernel_size = 1 로 지정
                    stride=stride,
                    bias=False,
                ),
                nn.BatchNorm2d(planes)                          # input 으로 맞는 크기의 데이터에 대해 적용할 수 있는 BatchNormalization 을 정의
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))                   # 앞에서 정의한대로 conv1 와 bn1 의 레이어를 거친 값에 relu 를 통과시킴
        out = self.bn2(self.conv2(out))                         # 앞에서 정의한 conv2 와 bn2 을 거친 값을 연산
        out += self.shortcut(x)                                 # 바로 위의 값과 shortcut 을 통과한 결과값을 더함. 이 부분을 skip connection 이라고 한다
        out = F.relu(out)                                       # shorcut 의 값을 계속 더한 값들에 relu 를 통과시켜 계산 된 결과값을 반환
        return out                                              # 최종적으로 out 을 반환하며, 이는 ResNet 내부에서 반복적으로 연산이 되는 Residual block 이라고 한다

class ResNet(nn.Module):
    def __init__(self, num_classes = 10):
        super(ResNet, self).__init__()

        self.in_planes = 16

        self.conv1 = nn.Conv2d(
            3,                                                  # 컬러이미지에 대응하는 filter
            16,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=False,
        )
        self.bn1 = nn.BatchNorm2d(16)
        self.layer1 = self._make_layer(16, 2, stride = 1)
        self.layer2 = self._make_layer(32, 2, stride = 2)
        self.layer3 = self._make_layer(64, 2, stride = 2)
        self.linear = nn.Linear(64, num_classes)

    def _make_layer(self, planes, num_blocks, stride):
        strides = [stride] + [1] * (num_blocks - 1)             # 인자값으로 주어지는 stride 를 이용해 stride 범위를 BasicBlock 마다 설정할 수 있도록 정의
        layers = list()                                         # BasicBlock 으로 생성 된 결과값을 저장해줄 리스트를 생성
    
        for stride in strides:                                  # stride 의 범위를 반복문의 범위로 지정
            layers.append(BasicBlock(
                self.in_planes,                                 # 반복문을 실행하면서 in_planes 값을 계속 업데이트 해 BasicBlock 을 새로 생성하기 위해 planes 값으로 업데이트
                planes, 
                stride))
            self.in_planes = planes
    
        return nn.Sequential(*layers)                           # 여러층으로 생성한 레이어를 nn.Sequential() 내에 정의해 반환시킴

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = F.avg_pool2d(out, 8)                          
        out = out.view(out.size(0), -1)                         # Average Pooling 을 거쳐 down sampling 된 feature map 에 대해 1차원의 벡터로 펼쳐줌 (flatten)
        out = self.linear(out)                                  # 위 과정을 거쳐 생성 된 값들을 10개의 노드로 구성 된 fully connected layer 에 연결
        return out

model = ResNet().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(
    model.parameters(),
    lr = 1e-3
)

def train(model, train_loader, optimizer, log_interval):
    model.train()

    for batch_idx, (image, label) in enumerate(train_loader):
        image = image.to(device)
        label = label.to(device)

        optimizer.zero_grad()
        output = model(image)
        loss = criterion(output, label)
        loss.backward()
        optimizer.step()

        if batch_idx % log_interval == 0:
            print(f'Epochs : {epoch} [{batch_idx * len(image)} / {len(train_loader.dataset)} ({100 * batch_idx / len(train_loader):.0f})%] Train Loss : {loss.item():.4f}')

def test(model, test_loader):
    model.eval()
    test_loss = 0
    correct = 0

    for image, label in test_loader:
        image = image.cuda()
        label = label.cuda()

        output = model(image)
        prediction = output.max(1, keepdim = True)[1]
        test_loss += criterion(output, label).item()
        correct += prediction.eq(label.view_as(prediction)).sum().item()

    test_loss /= len(test_loader.dataset)
    accuracy = 100 * correct / len(test_loader.dataset)

    return test_loss, accuracy

for epoch in range(1, 11):
    print(f'Epochs : {epoch}\n')
    train(model, train_loader, optimizer, log_interval=200)
    test_loss, accuracy = test(model, test_loader)
    print(f'\nTest Loss : {test_loss:.4f} \t Accuracy : {accuracy:.0f} %\n')

print(str_time - datetime.datetime.now())
