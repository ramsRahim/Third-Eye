import time

import torch
import numpy as np
from torchvision import models, transforms

import cv2
from PIL import Image
import ast



# Read the labels

with open('./label.txt','r') as f:
        class_labels_str = f.read()
        class_labels_dict = ast.literal_eval(class_labels_str)

class_labels = [class_labels_dict[key] for key in sorted(class_labels_dict)]

torch.backends.quantized.engine = 'qnnpack'

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 224)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 224)
cap.set(cv2.CAP_PROP_FPS, 36)

preprocess = transforms.Compose([
#    transforms.Resize(32),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

net = models.quantization.mobilenet_v2(weights='DEFAULT')
#net = models.resnet18(pretrained=True)
net.eval()
#net = models.mobilenet_v2(pretrained=True)

# jit model to take it from ~20fps to ~30fps
net = torch.jit.script(net)

started = time.time()
last_logged = time.time()
frame_count = 0

with torch.no_grad():
    while True:
        # read frame
        ret, image = cap.read()
        if not ret:
            raise RuntimeError("failed to read frame")

        # convert opencv output from BGR to RGB
        image = image[:, :, [2, 1, 0]]
        permuted = image

        # preprocess
        input_tensor = preprocess(image)
        #print(input_tensor.shape)

        # create a mini-batch as expected by the model
        input_batch = input_tensor.unsqueeze(0)

        # run model
        outputs = net(input_batch)
        #print(type(output))
        probabilities = torch.nn.functional.softmax(outputs[0],dim=0)
        _,predicted_class = torch.max(probabilities,0)
        predicted_label = class_labels[predicted_class.item()]
        print(predicted_label)
        # do something with output ...

        # log model performance
        # frame_count += 1
        # now = time.time()
        # if now - last_logged > 1:
        #     print(f"{frame_count / (now-last_logged)} fps")
        #     last_logged = now
        #     frame_count = 0
        cv2.imshow('image', image)
        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
