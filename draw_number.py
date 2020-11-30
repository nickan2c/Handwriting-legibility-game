 https://www.python-course.eu/tkinter_events_binds.php

from tkinter import *
import PIL
from PIL import Image, ImageGrab
import time

class drawing:
    def __init__(self, prompt):  # prompt is the number that the user should draw
        self.root = Tk()  # initiate window
        Label(text=('draw a {}'.format(prompt))).pack()
        self.lastx, self.lasty = None, None  # at this point, user hasn't clicked yet so defined as none
        self.canvas = Canvas(self.root, width=280, height=280)  # width and height based on the 28x28 required mnist size

        self.seconds = 4
        Label(text=('you have {} seconds'.format(seconds))).pack()

        self.canvas.bind('<Button-1>',
                         self.activate_paint)  # button 1 is mouse left click, binded so that every time mouse left click is
        # called, activate_paint function is also called
        self.canvas.pack()

        submit_button = Button(text="submit", command=self.submit)
        submit_button.pack()

        self.root.mainloop()

    def submit(self):
        x = self.root.winfo_rootx() + self.canvas.winfo_x()  # gets left x coordinate
        y = self.root.winfo_rooty() + self.canvas.winfo_y() # gets top y coordinate
        x1 = x + self.canvas.winfo_width()  # gets right side x coordinate by adding width to leftmost x coordinate
        y1 = y + self.canvas.winfo_height()  # gets bottom y coordinate by adding height to top y coordinate
        ImageGrab.grab().crop((x, y, x1, y1)).save('drawing.png') # imagegrab.grab 'screenshots' at those coordinates

        print('image saved')

    def activate_paint(self, event):  # event is passed in from canvas.bind, where
        self.canvas.bind('<B1-Motion>', self.paint)  # when mouse is moved while left click is held, it paints
        self.lastx, self.lasty = event.x, event.y

    def paint(self, event):
        self.x_co, self.y_co = event.x, event.y
        self.canvas.create_line((self.lastx, self.lasty, self.x_co, self.y_co), width=5)

        self.lastx, self.lasty = self.x_co, self.y_co  # redefine last x last y as point where user clicked


import random
num_games = 0  # will be selected by user
d = drawing(6)



