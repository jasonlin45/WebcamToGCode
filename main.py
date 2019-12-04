import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time
import numpy
from gcode_gen import create_abs_gcode
from gcode_gen import create_rel_gcode

class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
 
        # open webcam
        self.vid = VideoCapture()

        
        # Create a canvas for input
        self.canvas = tk.Canvas(window, width = self.vid.width, height = self.vid.height)
        in_label = tk.Label(window, text="Webcam Input", font=("Helvetica", 16))
        in_label.grid(row=0, column=0)
        self.canvas.grid(row=1, column=0, rowspan=3)

        # Create an output preview
        self.preview = tk.Canvas(window, width = self.vid.width, height = self.vid.height)
        out_label = tk.Label(window, text="Estimated Output", font=("Helvetica", 16))
        out_label.grid(row=0, column=1)
        self.preview.grid(row=1, column=1, rowspan=3)
        
        # Options pane -----------------------------------------------------------
        options_label = tk.Label(window, text="Options", font=("Helvetica", 16))
        options_label.grid(row=0, column=2, columnspan=2)
        # Create radio buttons for choosing blackwhite mode/channel
        options = [
            ("Default", 0),
            ("Red", 1),
            ("Green", 2),
            ("Blue", 3),
        ]

        self.mode = tk.IntVar()
        self.mode.set(0)
        frame = tk.Frame(window, relief="flat")
        color_label = tk.Label(frame, text="Choose a Color Mode", font=("Helvetica", 12), relief="flat", underline=1)
        color_label.pack()
        for text, option in options:
            self.channels = tk.Radiobutton(frame, text=text, variable=self.mode, value=option)
            self.channels.pack(anchor=tk.W)
        frame.grid(row=1, column = 2, columnspan = 2)

        # Create slider for adjusting output threshold
        tfrm = tk.Frame(window, relief="flat")
        thresh_label = tk.Label(tfrm, text="Threshold", font=("Helvetica", 12), relief="flat")
        thresh_label.pack()
        self.slider = tk.Scale(tfrm, from_=0, to=255, orient=tk.HORIZONTAL, length=150)
        self.slider.set(127)
        self.slider.pack()
        tfrm.grid(row=2, column=2, columnspan = 2)
        # Create a button to invert output
        self.inv = False
        self.inv_button = tk.Button(window, text="Invert", width=30, command=self.invert, font = ("Helvetica", 12), relief = "raised")
        self.inv_button.grid(row=3, column=2, columnspan=2)
        
        # Snapshot button
        self.btn_snapshot=tk.Button(window, text="Generate GCode!", width=50, command=self.snapshot, font=("Helvetica", 16), bg="#4be39f", relief = "solid")
        self.btn_snapshot.grid(row=4, columnspan=2, pady=10)
 
        # 15 millisecond delay (approx 60 fps)
        self.delay = 15
        self.update()
 
        self.window.mainloop()

    def invert(self):
        self.inv = not self.inv
        if(self.inv):
            self.inv_button.config(relief = "sunken")
        else:
            self.inv_button.config(relief = "raised")

    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            tmp_file_name = str(time.strftime("%d-%m-%Y-%H-%M-%S"))
            cv2.imwrite(tmp_file_name + ".png", self.blackWhite)
            create_abs_gcode(self.blackWhite, tmp_file_name, 100, 0.5)
            create_rel_gcode(self.blackWhite, tmp_file_name, 100, 0.5)
            

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
         
        if ret:
            self.image = cv2.cvtColor(frame, cv2.cv2.COLOR_RGB2BGR)
            self.grey = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            self.b, self.g, self.r = cv2.split(self.image)
            m = self.mode.get()
            if(m==1):
                self.grey = self.r
            elif(m==2):
                self.grey = self.g
            elif(m==3):
                self.grey = self.b
            if(self.inv):
                self.grey = cv2.bitwise_not(self.grey)
            
            (thresh, self.blackWhite) = cv2.threshold(self.grey, self.slider.get(), 255, cv2.THRESH_BINARY)

            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.bw = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.blackWhite))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
            self.preview.create_image(0, 0, image = self.bw, anchor = tk.NW)
 
        self.window.after(self.delay, self.update)

 
class VideoCapture:
    def __init__(self):
        # Open default webcam
        self.vid = cv2.VideoCapture(0)
        if not self.vid.isOpened():
            raise ValueError("Unable to open webcam", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
 
# run the app!
App(tk.Tk(), "Webcam to GCode")