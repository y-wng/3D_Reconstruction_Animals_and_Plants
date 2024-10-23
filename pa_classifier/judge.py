import torch
from torchvision import models, transforms
from PIL import Image
import requests
import os
import re

# 下载 ImageNet 的类别标签
# LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
# labels = requests.get(LABELS_URL).text.splitlines()


def read_labels():
    labels = []
    file_path = './pa_classifier/image1k.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        labels.extend(content.splitlines())
    return labels


labels = read_labels()

# 加载预训练模型
model = models.efficientnet_b7(pretrained=True)
model.eval()

# 定义图片预处理过程
preprocess = transforms.Compose([
    transforms.Resize(256),  # 调整大小
    transforms.CenterCrop(224),  # 裁剪中心区域
    transforms.ToTensor(),  # 转换为Tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # 标准化
])

def is_animal_label(catid):
    """判断类别编号是否属于动物范围"""
    plant_or_animal_ranges = [(0, 397), (973, 973)]
    for start, end in plant_or_animal_ranges:
        if start <= catid <= end:
            return True
    return False
def is_plants_label(catid):
    """判断类别编号是否属于植物范围"""
    plant_or_animal_ranges = [(936, 957), (984, 998), (738, 738)]
    for start, end in plant_or_animal_ranges:
        if start <= catid <= end:
            return True
    return False
def is_plant_or_animal_label(catid):
    """判断类别编号是否属于动植物范围"""
    # 动植物的标签编号范围
    plant_or_animal_ranges = [(0, 397), (936, 957), (984, 998), (738, 738), (973, 973)]
    for start, end in plant_or_animal_ranges:
        if start <= catid <= end:
            return True
    return False


def find_view_files(path):
    pattern = re.compile(r'view_(\d+)\.png')
    return [f for f in os.listdir(path) if pattern.match(f)]


def predict_image(path, k):
    image = Image.open(path)
    # 如果图像是 PNG 格式且包含透明通道，将其转换为 RGB 模式
    if image.mode != 'RGB':
        image = image.convert('RGB')
    img_tensor = preprocess(image).unsqueeze(0)

    with torch.no_grad():
        output = model(img_tensor)
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    topk_prob, topk_catid = torch.topk(probabilities, k)
    max_prob, max_catid = torch.topk(probabilities, 1)
    max_class = labels[max_catid]
    is_plant_or_animal = False
    plant_or_animal = False
    topk_labels = []
    for i in range(topk_catid.size(0)):
        predicted_label = labels[topk_catid[i]]
        topk_labels.append(predicted_label)
        if is_plant_or_animal_label(topk_catid[i].item()):
            is_plant_or_animal = True
        if is_animal_label(topk_catid[i].item()):
            plant_or_animal = True
    if is_plant_or_animal:
        result = f"The image is likely a plant or animal based on the Top {k} predictions: {topk_labels}"
    else:
        result = f"The image is likely not a plant or animal. Top {k} predictions: {topk_labels}"
    print(result)

    return plant_or_animal, is_plant_or_animal, [max_prob, max_class]


def is_PA(k, path):
    view_files = find_view_files(path)
    num_true = 0
    num_false = 0
    max_prob = 0
    plant_or_animal_true = 0
    plant_or_animal_False = 0
    for f in view_files:
        img_path = os.path.join(path, f)
        plant_or_animal, flag, max_class = predict_image(img_path, k)
        if flag:
            num_true += 1
        else:
            num_false += 1
        if plant_or_animal:
            plant_or_animal_true += 1
        else:
            plant_or_animal_False += 1
        if max_class[0] > max_prob:
            max_prob = max_class[0]
            pred = max_class[1]
    
    if num_true > num_false:
        if plant_or_animal_true > plant_or_animal_False:
            result = f"The image is likely a animal based on the Top {k} predictions.species:animal," + "\n" + \
                 f"According to Img1k dataset, it is most likely to be {pred}."
        else:
            result = f"The image is likely a plant based on the Top {k} predictions. species:plant," + "\n" + \
                 f"According to Img1k dataset, it is most likely to be {pred}."
        return True, result
    else:
        result = f"The image is likely not a plant or animal."
        return False, result
