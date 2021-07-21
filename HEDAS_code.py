from tkinter import * 
from tkinter import messagebox
import PIL
from PIL import Image,ImageTk
from numpy.lib.function_base import angle
import socket
import serial
import serial.tools.list_ports
from threading import Thread
from time import sleep
import numpy as np
import trace
import json
import sys
import os
import cv2

# creates a Tk() object
master = Tk()

#global variables
ready = False
arduino = ""
angles_raw = [0]*19
angles = [0]*23
unity = False
done = True
val = 0
sock =0
button_web = 0
# Variables for calibration
angle_calibration = [0,45,90]
angle_calibration_thumb = [0,45,80]
angle_calibration_wrist = [-45,0,45]
x_MCP = [[0] * 3 for i1 in range(5)]
x_PIP = [[0] * 3 for i1 in range(5)]
z_MCP = [0]*7
wrist_val = [0] * 3
coeff_MCP = [[0] * 3 for i1 in range(5)]
coeff_PIP = [[0] * 3 for i1 in range(5)]
coeff_wrist = [0] * 3

#webcam variables
start_point_45 = [(400,400),(400,300),(365,265)]
end_point_45 = [(400,300),(365,265),(315,265)]

start_point_90 = [(400,400),(400,300),(350,300)]
end_point_90 = [(400,300),(350,300),(350,350)]

color_prox = (255, 255, 0)
color_meta = (0, 255, 0)
color_hand = (0, 0, 255)

alpha = 0.4
thickness = 10
show_cam = False
cap = 0
#----------------------------function/thread for the interface--------------------------#
# 1) Main page: asking for the Port to which the Arduino is connected
def interface():
    global master
    master.title("H.E.D.A.S (Hand Exoskeleton Data Acquisition System)")
    master.state('zoomed')
    master.config(bg = 'medium aquamarine')

    ports = serial.tools.list_ports.comports(include_links=False) #looking for the acive ports

    if (len(ports) != 0): # we found a port
        label = Label(master, text ="Choose the port to which the device is connected:", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack(pady = 150)
        for port in ports :  # we display the ports' name on buttons
            Button(master, text = port.device, command = lambda : Calibration(port.device), font=("Abadi MT Condensed Extra Bold", 30), bg = 'snow').pack()
    else:  # else we need to connect the device and relaunch the program
        label = Label(master, text = "No port found. Connect a device and relaunch the program", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack(pady = 300)

# 2) Page where there is a choice between calibrating and using a previous calibration      
def Calibration(portDevice):
    global master,ready,arduino
    arduino = serial.Serial(port=portDevice, baudrate=115200, timeout=.1) # the arduino is connected to Python
    ready = True # the read_function can start reading the Arduino data
    eraseWidget()
    if os.path.isfile(os.path.join(path + os.sep, "sample.json")):
        Label(master, text ="Do you want to calibrate or use a previous calibration profile?", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack(pady = 150)
        Button(master, text = "New calibration", command = calibration, font=("Abadi MT Condensed Extra Bold", 30), bg = 'snow').pack(pady = 10)
        Button(master, text = "Use a user calibration profile", command = NoCal, font=("Abadi MT Condensed Extra Bold", 30), bg = 'snow').pack(pady = 50)
    else:
        Label(master, text ="You didn't calibrate yet... Create a new calibration", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack(pady = 150)
        Button(master, text = "New calibration", command = calibration, font=("Abadi MT Condensed Extra Bold", 30), bg = 'snow').pack(pady = 10)

# 3) Calibration process
def calibration():
    global master, val, show_cam,cap,thread1, button_web
    eraseWidget()

    if val == 0:
        Label(master, text ="Put your hand flat with the thumb as far as possible from the fingers", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack()
        image1 = Image.open(os.path.join(path + os.sep, "0 above.jpg"))
        image1 = image1.resize((800, 600), Image.ANTIALIAS)
        test = ImageTk.PhotoImage(image1)
        label1 = Label(image=test, bg = 'medium aquamarine')
        label1.image = test
        label1.pack(side = TOP, pady = 25)

    if val == 1:
        Label(master, text ="Close your hand so that all your figner and thumb joints are forming a 45° angle", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack()
        image1 = Image.open(os.path.join(path + os.sep, "45 profile.jpg"))
        image1 = image1.resize((720, 540), Image.ANTIALIAS)
        test1 = ImageTk.PhotoImage(image1)
        label1 = Label(image=test1, bg = 'medium aquamarine')
        label1.image = test1
        label1.place(x=400,y = master.winfo_height()/2,anchor = CENTER)
        Label(master, text ="Wait...", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2,anchor = CENTER)
        if not show_cam:
            Button(master, text = "Show the webcam", command = lambda : show(), font=("Abadi MT Condensed Extra Bold", 30), bg = 'snow').place(x=1150,y = master.winfo_height()/2,anchor = CENTER)
            Label(master, text ="This will return the video of your webcam (if you have a one) ", font=("Abadi MT Condensed Extra Bold", 10), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2+50,anchor = CENTER)
            Label(master, text ="An indicator will show on the video to help you positioning your fingers", font=("Abadi MT Condensed Extra Bold", 10), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2+70,anchor = CENTER)
            Label(master, text ="Opening the webcam can take a couple of seconds", font=("Abadi MT Condensed Extra Bold", 10), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2+90,anchor = CENTER)
        

    if val == 2:
        Label(master, text ="Close your hand so that all your figner and thumb joints are forming a 90° angle", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack()
        image1 = Image.open(os.path.join(path + os.sep, "90 profile.jpg"))
        image1 = image1.resize((720, 540), Image.ANTIALIAS)
        test1 = ImageTk.PhotoImage(image1)
        label1 = Label(image=test1, bg = 'medium aquamarine')
        label1.image = test1
        label1.place(x=400,y = master.winfo_height()/2,anchor = CENTER)
        Label(master, text ="Wait...", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2,anchor = CENTER)
        if not show_cam:
            Button(master, text = "Show the webcam", command = lambda : show(), font=("Abadi MT Condensed Extra Bold", 30), bg = 'snow').place(x=1150,y = master.winfo_height()/2,anchor = CENTER)
            Label(master, text ="This will return the video of your webcam (if you have a one) ", font=("Abadi MT Condensed Extra Bold", 10), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2+50,anchor = CENTER)
            Label(master, text ="An indicator will show on the video to help you positioning your fingers", font=("Abadi MT Condensed Extra Bold", 10), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2+70,anchor = CENTER)
            Label(master, text ="Opening the webcam can take a couple of seconds", font=("Abadi MT Condensed Extra Bold", 10), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2+90,anchor = CENTER)
    if val == 3:
        Label(master, text ="Fold your wrist until your hand forms a -45° angle with your arm", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack()
        image1 = Image.open(os.path.join(path + os.sep, "90 profile.jpg"))
        image1 = image1.resize((720, 540), Image.ANTIALIAS)
        test1 = ImageTk.PhotoImage(image1)
        label1 = Label(image=test1, bg = 'medium aquamarine')
        label1.image = test1
        label1.place(x=400,y = master.winfo_height()/2,anchor = CENTER)
        Label(master, text ="Wait...", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2,anchor = CENTER)
        if not show_cam:
            Button(master, text = "Show the webcam", command = lambda : show(), font=("Abadi MT Condensed Extra Bold", 30), bg = 'snow').place(x=1150,y = master.winfo_height()/2,anchor = CENTER)
            Label(master, text ="This will return the video of your webcam (if you have a one) ", font=("Abadi MT Condensed Extra Bold", 10), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2+50,anchor = CENTER)
            Label(master, text ="An indicator will show on the video to help you positioning your fingers", font=("Abadi MT Condensed Extra Bold", 10), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2+70,anchor = CENTER)
            Label(master, text ="Opening the webcam can take a couple of seconds", font=("Abadi MT Condensed Extra Bold", 10), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2+90,anchor = CENTER)
    if val == 4:
        Label(master, text ="Fold your wrist the other way until your hand forms a 45° angle with your arm", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack()
        image1 = Image.open(os.path.join(path + os.sep, "90 profile.jpg"))
        image1 = image1.resize((720, 540), Image.ANTIALIAS)
        test1 = ImageTk.PhotoImage(image1)
        label1 = Label(image=test1, bg = 'medium aquamarine')
        label1.image = test1
        label1.place(x=400,y = master.winfo_height()/2,anchor = CENTER)
        Label(master, text ="Wait...", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2,anchor = CENTER)
        if not show_cam:
            Button(master, text = "Show the webcam", command = lambda : show(), font=("Abadi MT Condensed Extra Bold", 30), bg = 'snow').place(x=1150,y = master.winfo_height()/2,anchor = CENTER)
            Label(master, text ="This will return the video of your webcam (if you have a one) ", font=("Abadi MT Condensed Extra Bold", 10), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2+50,anchor = CENTER)
            Label(master, text ="An indicator will show on the video to help you positioning your fingers", font=("Abadi MT Condensed Extra Bold", 10), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2+70,anchor = CENTER)
            Label(master, text ="Opening the webcam can take a couple of seconds", font=("Abadi MT Condensed Extra Bold", 10), bg = 'medium aquamarine').place(x=1150,y = master.winfo_height()/2+90,anchor = CENTER)
    # We ask for a name
    if val == 5:
        if show_cam:
            cap.release()
            thread1.kill()
        Label(master, text="Enter your calibration name", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack()
        entry1 = Entry(master, font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine')
        entry1.pack()
        Button(master, text = "Submit!", command = lambda : getName(entry1.get()), font=("Abadi MT Condensed Extra Bold", 30), bg = 'snow').pack()
        
    if val<5:
        Button(master, text = "Done!", command = lambda : get_calibration(), font=("Abadi MT Condensed Extra Bold", 30), bg = 'snow').place(x=725, y=700)

# 3.1) Function that collects the data necessary to estimate the angle from the potentiometer values
def get_calibration():
    global angles_raw, val,coeff_MCP,coeff_PIP,coeff_wrist,wrist_val
    eraseWidget()
    if val==0:
        wrist_val[1] = angles_raw[18]
        for i in range(0,7):
            z_MCP[i] = angles_raw[i+10]
    if val < 3 :
        for j in range(0,5):
            x_PIP[j][val] = angles_raw[j]
            x_MCP[j][val] = angles_raw[j+5]
    
    if val == 3:
        wrist_val[0] = angles_raw[18]

    if val == 4:
        wrist_val[2] = angles_raw[18]

    val = val + 1
    if val == 5:
        for t in range(0,5):
            coeff_MCP[t] = np.polyfit(x_MCP[t],angle_calibration,2).tolist()
            coeff_PIP[t] = np.polyfit(x_PIP[t],angle_calibration,2).tolist()
        coeff_MCP[0] = np.polyfit(x_MCP[0],angle_calibration_thumb,2).tolist()
        coeff_wrist = np.polyfit(wrist_val,angle_calibration_wrist,2).tolist()
    calibration() # it always goes back to the calibration function

def show():
    global show_cam,cap
    show_cam = True
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    thread1.start()
    calibration()

#3.2) ONce the calibration is finished, the program needs to save the data in a JSON file
def getName(name):
    global coeff_MCP, coeff_PIP, z_MCP, coeff_wrist
    if os.path.isfile(os.path.join(path + os.sep, "sample.json")): # it verifies if a file already exists 
        with open(os.path.join(path + os.sep, "sample.json")) as json_open: # if there exists one, it opens it
            data = json.load(json_open)
            
        data['Usernames'].append({'name': name,'PIP': coeff_PIP,'MPCx': coeff_MCP,'MPCz': z_MCP,'wrist': coeff_wrist})

        with open(os.path.join(path + os.sep, "sample.json"),"w") as json_write:
            json.dump(data,json_write)

    else: # otherwise we create a file in the directory of the program
        data = {}
        data['Usernames'] = []
        data['Usernames'].append({'name': name,'PIP': coeff_PIP,'MPCx': coeff_MCP,'MPCz': z_MCP,'wrist': coeff_wrist})

        with open(os.path.join(path + os.sep, "sample.json"), "w") as json_create:
            json.dump(data, json_create)

    final_page() # Finally, the code arrives to the final page

# 4) It is called if the user choose to use a previous calibration
def NoCal():
    eraseWidget()
    Label(master, text ="Choose your calibration profile", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack(pady = 100)
    with open(os.path.join(path + os.sep, "sample.json")) as json_open:
        data = json.load(json_open)
    for user in data['Usernames'] : 
        Button(master, text = user['name'], command = lambda username = user: get_coeff(username['PIP'],username['MPCx'],username['MPCz'],username['wrist']), font=("Abadi MT Condensed Extra Bold", 30), bg = 'snow').pack(pady = 10)

# Function that replace the coefficient from the JSON
def get_coeff(PIP, MPCx, MPCz,wrist):
    global coeff_MCP, coeff_PIP, z_MCP, coeff_wrist
    coeff_PIP = PIP
    coeff_MCP = MPCx
    z_MCP = MPCz
    coeff_wrist = wrist
    final_page()

# 5) The final page just display a message
def final_page():
    #comment this line if you don't want a connection to Unity
    Unity()
    eraseWidget()
    Label(master, text ="You are ready to use the glove", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack(pady = 150)
    Label(master, text ="The angles are avaibles in the array 'angles'", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack(pady = 10)
    Label(master, text ="Or try in UNITY", font=("Abadi MT Condensed Extra Bold", 30), bg = 'medium aquamarine').pack()

# If called, it connects to the socket of Unity
def Unity():
    global unity,sock
    unity = True
    host, port = "127.0.0.1", 25001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

#----A class that allows a function/thread to be closed if it's an infinity loop---#
class thread_with_trace(Thread):
  def __init__(self, *args, **keywords):
    Thread.__init__(self, *args, **keywords)
    self.killed = False
  
  def start(self):
    self.__run_backup = self.run
    self.run = self.__run      
    Thread.start(self)
  
  def __run(self):
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup
  
  def globaltrace(self, frame, event, arg):
    if event == 'call':
      return self.localtrace
    else:
      return None
  
  def localtrace(self, frame, event, arg):
    if self.killed:
      if event == 'line':
        raise SystemExit()
    return self.localtrace
  
  def kill(self):
    self.killed = True

#---------------function that treats, arranges and send the data----------------#
def read_function():
    global ready,angles_raw,angles,unity,sock
    while True:
        if ready == True:
            data = arduino.readline()[:-2]
            if data:

                angles_raw = [float(x) for x in data.split()] 
                
                for i in range (0,5):
                    # PIP
                    angles[i] = poly_reg(coeff_PIP[i], angles_raw[i])
                    # MCPx
                    angles[i+5]= poly_reg(coeff_MCP[i], angles_raw[i+5])
                
                for i in range (0,7):
                    # MCPz
                    angles[i+10] = potToAngle(z_MCP[i])-potToAngle(angles_raw[i+10])
                
                #wirst values
                angles[17] = potToAngle(angles_raw[17])-180
                angles[18] = poly_reg(coeff_wrist, angles_raw[18])

                for i in range (0,4): 
                    # DIP
                    angles[i+19] = angles[i+1]*0.88

                print("MPCx angle: ",angles[6])
                
                if unity:
                    for i in range (0,23):
                        angles[i] = int(angles[i]*1000)
                    sock.sendall(json.dumps(angles).encode())
                

def show_image():
    global show_cam,val,start_point_45,end_point_45,start_point_90,end_point_90
    while True:
        if show_cam:
            _, frame = cap.read()
            frame = cv2.flip(frame, 1)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            overlay = cv2image.copy()
            if val == 1:
                cv2.line(overlay, start_point_45[0], end_point_45[0], color_hand, thickness)
                cv2.line(overlay, start_point_45[1], end_point_45[1], color_meta, thickness)
                cv2.line(overlay, start_point_45[2], end_point_45[2], color_prox, thickness)
            if val == 2:
                cv2.line(overlay, start_point_90[0], end_point_90[0], color_hand, thickness)
                cv2.line(overlay, start_point_90[1], end_point_90[1], color_meta, thickness)
                cv2.line(overlay, start_point_90[2], end_point_90[2], color_prox, thickness)
            cv2.addWeighted(overlay, alpha, cv2image, 1 - alpha,0, cv2image)
            img = PIL.Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            label2 = Label(image=imgtk, bg = 'medium aquamarine')
            label2.image = imgtk
            label2.place(x=1150,y = master.winfo_height()/2,anchor = CENTER)

#----------general functions--------# 
def on_closing():
    global cap,show_cam
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if show_cam:
            cap.release()
            thread1.kill()
        thread.kill()
        master.quit()

def eraseWidget():
    for widgets in master.winfo_children():
        widgets.destroy()

def poly_reg(coeff,val):
    return coeff[0] * pow(val,2) + coeff[1]*val + coeff[2]

def potToAngle(val):
    return val * 330 / 1023 + 30

# Main where the Threads are started
if __name__ == "__main__":
    thread1 = thread_with_trace(target = show_image)
    thread = thread_with_trace(target = read_function)
    thread2 = Thread(target = interface)
    path = os.path.dirname(os.path.abspath(__file__))
    thread2.start()
    thread.start()
    master.protocol("WM_DELETE_WINDOW", on_closing)
    master.mainloop()