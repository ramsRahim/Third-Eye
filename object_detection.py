import time

import torch
import numpy as np
from torchvision import models, transforms

import cv2
from PIL import Image

torch.backends.quantized.engine = 'qnnpack'

# Initialize the camera capture object with the cv2.VideoCapture class.
# The '0' denotes that we want to use the first camera device.
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 224)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 224)
cap.set(cv2.CAP_PROP_FPS, 36)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

preprocess = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

net = models.quantization.resnet18( weights='DEFAULT', quantize=False)
# jit model to take it from ~20fps to ~30fps
#net = torch.jit.script(net)

started = time.time()
last_logged = time.time()
frame_count = 0

try:
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        # convert opencv output from BGR to RGB
        image = frame[:, :, [2, 1, 0]]
        #permuted = image
        
        # preprocess
        input_tensor = preprocess(image)

        # create a mini-batch as expected by the model
        input_batch = input_tensor.unsqueeze(0)

        # run model
        #output = net(input_batch)
        # do something with output ...

        # log model performance
        # frame_count += 1
        # now = time.time()
        # if now - last_logged > 1:
        #     print(f"{frame_count / (now-last_logged)} fps")
        #     last_logged = now
        #     frame_count = 0
            
        # Display the resulting frame
        cv2.imshow('frame', frame)

        # Press 'q' to exit the video stream
        if cv2.waitKey(1) == ord('q'):
            break
except KeyboardInterrupt:
    # Handle any other exit commands like CTRL+C gracefully.
    print("Stream stopped")

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
