# Third-Eye

1. run ```bash
   python classifier.py```   
it will pull up the camera and detect objects that are in front of the camera.   
   
2. then run ```bash
   sudo python lora_sender.py```   
We are using sudo because it will need sudo access to access the node of the raspberry pi.Here I am using sudo because it will need sudo access to access the node of the raspberry pi. This script basically sends the labels that are detected from the objection model to the receiver Node.
  
   
   
3. then run ```bash
   sudo python lora_reciever.py``` on another pi.     
You will be able to see the labels that are being sent by the sender Node.
