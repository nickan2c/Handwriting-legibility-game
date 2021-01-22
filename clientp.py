# import pygame
from networkp import Network
from tkinter import *
from PIL import Image, ImageFilter, EpsImagePlugin

import numpy as np
import random


class draw:
    def __init__(self, prompt, attempt_number):  # prompt is the number that the user should draw
        self.root = Tk()  # initiate window
        self.attempt_number = attempt_number
        Label(self.root, text=('draw: {}'.format(prompt)), font=('American typewriter ', 30)).pack()

        self.lastx, self.lasty = None, None  # at this point, user hasn't clicked yet so defined as none
        self.canvas = Canvas(self.root, width=280, height=280)  # based on the 28x28 required mnist size

        seconds = 4
        try:
            self.root.after(4000, self.submit)  # after 4 seconds submit whatever is on screen
            Label(self.root, text=('You have {} seconds'.format(seconds))).pack()
        except:  # after 4 seconds, It submits. However user can press submit to submit before this, which gives an
            # error that it was already closed.
            pass
        self.canvas.bind('<Button-1>',
                         self.activate_paint)  # button 1 is mouse left click, binded so that every time mouse left
        # click is called, activate_paint function is also called
        self.canvas.pack()

        submit_button = Button(self.root, text="submit", command=self.submit)
        submit_button.pack()

        self.root.mainloop()

        self.submitted = False

    def submit(self):
        self.submitted = True
        self.canvas.postscript(file='drawing.eps')
        # Used https://stackoverflow.com/questions/9886274/how-can-i-convert-canvas-content-to-an-image

        # I was able to get the contents of the canvas, by using the built in ‘canvas.postscript’ method of tkinter,
        # which returns the canvas object as an image. Then I am able to use the module PIL  to convert that into a
        # png file, which I can save.

        EpsImagePlugin.gs_windows_binary = r'C:\Program Files\gs\gs9.53.3\bin\gswin64c' # this line was used in order to
        # fix an error I was having, where the ghostscript file used in Image.open wasn't found
        img = Image.open("drawing.eps")
        img.save(f"drawing{self.attempt_number}.png", "png")  # saves file using f string. ie it will be drawing1,
        # drawing2, etc. This way i can retrieve the images later, as before it would just save to drawing.png each time

        self.root.destroy()

    def activate_paint(self, event):
        '''
        event is passed in from canvas.bind by default
        when mouse is moved while left click is held, it paints
        '''
        self.canvas.bind('<B1-Motion>', self.paint)
        self.lastx, self.lasty = event.x, event.y

    def paint(self, event):
        self.x_co, self.y_co = event.x, event.y
        self.canvas.create_line((self.lastx, self.lasty, self.x_co, self.y_co), width=5)

        self.lastx, self.lasty = self.x_co, self.y_co  # redefine last x last y as point where user clicked


class drawing:
    def __init__(self, prompt, game_num, name='drawing0.png'):
        self.prompt = prompt
        self.game_num = game_num
        self.drawn = None
        self.correct = False
        self.certainty = 0
        self.mnist = np.array(self.prepare(name))

    def eval(self, correct, certainty):
        self.correct = correct
        self.certainty = certainty

    def prepare(self, image):
        im = Image.open(image).convert('L')  # opens the image in greyscale format, black and white
        new_image = Image.new('L', (28, 28), 255)  # creates white canvas of 28x28 pixels, for later use

        img = im.resize((20, 20), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)  # resizes the image to make it 20x20,
        # as per the mnist dataset standard. Antialias is used to smooth the image out, and sharpen sharpens it
        h_pos = 4  # horizontal position. original width - new width /2 (so that it can be centered)
        #  or in other words (28 - 20) / 2
        v_pos = 4  # vertical position. Same reasoning as horizontal

        new_image.paste(img, (v_pos, h_pos))  # puts this image on top of the white canvas created earlier
        pixel_values = list(new_image.getdata())  # get pixel values

        normalised_values = [(255 - val) / 255.0 for val in pixel_values]  # 255 - x inverts the colour,
        # /255 normalises it to be between 0 and 1
        return normalised_values


def main():
    num_games = 1
    n = Network()

    for game_num in range(num_games):
        prompt = random.randint(0, 9)
        draw(prompt, game_num)
        name = f'drawing{game_num}.png'
        d = drawing(prompt, game_num, name)

        perc_certain, guess = n.send(d)

        print(f"I'm {perc_certain}% sure that that's a {guess} ")
        # p.move()
        # redrawWindow(win, p, p2)


print('hello?')
main()
