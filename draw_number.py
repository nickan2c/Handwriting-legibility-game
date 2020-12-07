 https://www.python-course.eu/tkinter_events_binds.php

from tkinter import *
import PIL
from PIL import Image, ImageGrab
import random

class drawing:
    def __init__(self, prompt, attempt_number):  # prompt is the number that the user should draw
        self.root = Tk()  # initiate window

        Label(text=('draw: {}'.format(prompt)), font=('American typewriter ', 30)).pack()

        self.lastx, self.lasty = None, None  # at this point, user hasn't clicked yet so defined as none
        self.canvas = Canvas(self.root, width=280, height=280)  # based on the 28x28 required mnist size

        self.seconds = 4
        self.root.after(4000, self.submit)  # after 4 seconds submit whatever is on screen
        Label(text=('You have {} seconds'.format(self.seconds))).pack()

        self.canvas.bind('<Button-1>',
                         self.activate_paint)  # button 1 is mouse left click, binded so that every time mouse left
        # click is called, activate_paint function is also called
        self.canvas.pack()

        submit_button = Button(text="submit", command=self.submit)
        submit_button.pack()

        self.root.mainloop()

        self.submitted = False

    def submit(self):
        self.submitted = True
        print(self.root.winfo_rootx())
        self.canvas.postscript(file='drawing.eps')  #
        # Used https://stackoverflow.com/questions/9886274/how-can-i-convert-canvas-content-to-an-image

        # I was able to get the contents of the canvas, by using the built in ‘canvas.postscript’ method of tkinter,
        # which returns the canvas object as an image. Then I am able to use the module PIL  to convert that into a
        # png file, which I can save.

        EpsImagePlugin.gs_windows_binary = r'C:\Program Files\gs\gs9.53.3\bin\gswin64c' # this line was used in order to
        # fix an error I was having, where the ghostscript file used in Image.open wasn't found
        img = Image.open("drawing.eps")
        img.save("drawing.png", "png")

        # somewhere, add to a list of the preprocessed imgs for this player
        self.root.destroy()

    def preprocess(self, img_name):
        pass

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

num_games = 1  # will be selected by user

for i in range(0, num_games):  # how many times game will be played
    prompt = random.randint(0, 9)
    d = drawing(prompt, i)  # passes in prompt ie what the user will draw and how many times they have drawn


def prepare_img(image):
    """
    Returns the pixel values of the .png input
    MNIST's images are black background with white ink for the drawing
    The images are made to fit in a 20x20 pixel box and they
    are centered in a 28x28
    """
    im = Image.open(image).convert('L') # opens the image in greyscale format, black and white
    new_image = Image.new('L', (28, 28), 255)  # creates white canvas of 28x28 pixels, for later use

    img = im.resize((20, 20), Image.ANTIALIAS).filter(ImageFilter.SHARPEN) # resizes the image to make it 20x20, as per
    # the mnist dataset standard. Antialias is used to smooth the image out, and sharpen sharpens it

    h_pos = 4  # horizontal position. original width - new width /2 (so that it can be centered)
    #  or in other words (28 - 20) / 2
    new_image.paste(img, (4, h_pos)) # puts this image on top of the white canvas created earlier
    pixel_values = list(new_image.getdata())  # get pixel values

    normalised_values = [(255 - val) / 255.0 for val in pixel_values]  # 255 - x inverts the colour,
    # /255 normalises it to be between 0 and 1
    return normalised_values


x = np.array(prepare_img('drawing.png'))

