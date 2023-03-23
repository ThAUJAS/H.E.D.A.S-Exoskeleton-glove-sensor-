# H.E.D.A.S The Exoskeleton glove sensor
This repo is the result of my master thesis for the Staffordshire University. The idea was to create a glove capable of measuring accurately the finger movements (almost every DOF) using cheap sensors (potentiometers). The structure of the glove is fully in 3D parts and assembled with some screws and bolts. The circuit is simple, yet very messy since we have a ton of potentiometers. The values are collected by an Arduino Nano and a multiplexer. Then, I used Unity to simulate a virtual hand, and see if the movements of my hand and the virtual one were corresponsing. 

**The repo is open source, you can Fork and modify as you wish my codes and my design.**

## How to use it
Launch the python script "HEDAS_code" to start the program. A window will open and you will:
- select the port to which the arudino is connected.
- choose whether you want to do another calibration or use a saved one.

The calibration is performed in 5 steps which requires different hand and fingers positions. You can choose to display the camera to help you calibrate. Then, save the calibration under a unique name.

## Requirements
- Tkinter (For the window display)
```
pip install tk
```
- OpenCV (Optional(webcam help for calibration))
```
pip3 install opencv-python
```

## What's included
They are a bunch of files here:
- **HEDAS_code.py** is the Python script. 
- **H.E.D.A.S.ino** is the Arduino code, just compile the file in the Arduino.
- *Sample.json* is the file where the calibrations are saved.
