import io
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from judge import find_view_files
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms as T
from torchvision import transforms, models
import json
import time

# load labels extracted from annotations to find at https://github.com/visipedia/inat_comp/tree/master/2021
with open('./pa_classifier/categories_inat2021.json') as f:
    categories = json.load(f)

model = None
use_gpu = False


def load_model():
    global model
    # TODO: Download pre-trained models from https://github.com/EibSReM/newt/tree/main/benchmark
    # TODO: adapt path to respective model
    model_weights_fp = './pa_classifier/inat2021_supervised_large_from_scratch.pth.tar'
    model = models.resnet50(pretrained=False)
    model.fc = torch.nn.Linear(model.fc.in_features, 10000)
    checkpoint = torch.load(model_weights_fp, map_location="cpu")
    model.load_state_dict(checkpoint['state_dict'], strict=True)
    model.eval()


def prepare_image(image, target_size):
    if image.mode != 'RGB':
        image = image.convert("RGB")

    # Resize the input image nad preprocess it.
    image = T.Resize(target_size)(image)
    image = T.ToTensor()(image)

    # Convert to Torch.Tensor and normalize.
    image = T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])(image)

    # Add batch_size axis.
    image = image[None]
    if use_gpu:
        image = image.cuda()
    return torch.autograd.Variable(image, volatile=True)


def predict(k, image_path):
    data = {"success": False}

    image = open(image_path, 'rb').read()
    image = Image.open(io.BytesIO(image))
    image = prepare_image(image, target_size=(224, 224))

    preds = F.softmax(model(image), dim=1)
    results = torch.topk(preds.cpu().data, k=k, dim=1)
    results = (results[0].cpu().numpy(), results[1].cpu().numpy())
    data['predictions'] = list()

    for prob, label in zip(results[0][0], results[1][0]):
        label_name = categories['categories'][label]['name']
        r = {"label": label_name, "probability": float(prob)}
        data['predictions'].append(r)
        # print(r)

    output_string = ''
    output_string = output_string + image_path + '\t'
    for (i, result) in enumerate(data['predictions']):
        output_string = output_string + '{}'.format(result['label']) + '\t' + '{:.4f}'.format(
            result['probability']) + '\t'

    return output_string, [results[0][0][0], results[1][0][0]]


def test(k, path):
    start = time.time()
    load_model()
    view_files = find_view_files(path)

    output_all = ''
    max_prob = 0
    for x in view_files:
        # print('this file is processed')
        # print(x)
        img_path = os.path.join(path, x)
        string, max_class = predict(k, img_path)
        output_all = output_all + string + '\n'
        if max_class[0] > max_prob:
            max_prob = max_class[0]
            max_label = max_class[1]

    end = time.time()
    total_time = end - start
    # print("classifier runtime: " + str(total_time))
    print(output_all)
    pred = categories['categories'][max_label]
    return pred

