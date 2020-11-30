# https://www.python-course.eu/tkinter_events_binds.php

from tkinter import *
import PIL
from PIL import Image, ImageDraw


class drawing:
    def __init__(self, prompt):  # prompt is the number that the user should draw
        root = Tk()  # initiate window
        self.prompt = Label(text=prompt)
        self.prompt.pack()
        self.lastx, self.lasty = None, None  # at this point, user hasn't clicked yet so defined as none
        self.canvas = Canvas(root, width=280, height=280)  # width and height based on the 28x28 required mnist size

        self.canvas.bind('<Button-1>',
                         self.activate_paint)  # button 1 is mouse left click, binded so that every time mouse left click is
        # called, activate_paint function is also called
        self.canvas.pack()

        submit_button = Button(text="submit", command=self.submit)
        submit_button.pack()

        root.mainloop()

    def submit(self):
        pass

    def activate_paint(self, event):  # event is passed in from canvas.bind, where
        self.canvas.bind('<B1-Motion>', self.paint)  # when mouse is moved while left click is held, it paints
        self.lastx, self.lasty = event.x, event.y

    def paint(self, event):
        self.x_co, self.y_co = event.x, event.y
        self.canvas.create_line((self.lastx, self.lasty, self.x_co, self.y_co), width=5)

        self.lastx, self.lasty = self.x_co, self.y_co  # redefine last x last y as point where user clicked


d = drawing()
