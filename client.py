from tkinter import *
from PIL import Image, ImageFilter, EpsImagePlugin
import random
from my_nn import NeuralNetwork, load_dataset
from networkp import *


class draw:
    def __init__(self, window, prompt, attempt_number):  # prompt is the number that the user should draw
        self.root = Tk()  # initiate window
        self.attempt_number = attempt_number
        self.window = window

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

        EpsImagePlugin.gs_windows_binary = r'C:\Program Files\gs\gs9.53.3\bin\gswin64c'  # this line was used in order to
        # fix an error I was having, where the ghostscript file used in Image.open wasn't found
        img = Image.open("drawing.eps")
        img.save(f"drawing{self.attempt_number}.png", "png")  # saves file using f string. ie it will be drawing1,
        # drawing2, etc. This way i can retrieve the images later, as before it would just save to drawing.png each time
        if self.attempt_number == 0:  # if windows have been destroyed, it would give an error that they cannot be
            # destroyed, so this only destroys on first round
            self.window.destroy()

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


def prepare_img(image):
    """
    Returns the pixel values of the .png input
    MNIST's images are black background with white ink for the drawing
    The images are made to fit in a 20x20 pixel box and they
    are centered in a 28x28
    """
    im = Image.open(image).convert('L')  # opens the image in greyscale format, black and white
    new_image = Image.new('L', (28, 28), 255)  # creates white canvas of 28x28 pixels

    img = im.resize((20, 20), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)  # resizes the image to make it 20x20, as per
    # the mnist dataset standard. Antialias is used to smooth the image out, and sharpen sharpens it
    h_pos = 4  # horizontal position. original width - new width /2 (so that it can be centered)
    #  or in other words (28 - 20) / 2
    v_pos = 4  # vertical position. Same reasoning as horizontal

    new_image.paste(img, (v_pos, h_pos))  # puts this image on top of the white canvas created earlier
    pixel_values = list(new_image.getdata())  # get pixel values

    normalised_values = [(255 - val) / 255.0 for val in pixel_values]  # 255 - x inverts the colour,
    # /255 normalises it to be between 0 and 1
    return normalised_values


class queue:  # used to select a prompt, and make sure the prompt isn't the same twice in a row
    def __init__(self, length):
        self.nums = []
        for i in range(1, length):
            self.nums.append(i)
        random.shuffle(self.nums)  # shuffles nums

    def refresh(self):
        self.last = self.dequeue()
        self.enqueue(self.last)
        return self.last

    def enqueue(self, item):
        self.nums.insert(0, item)  # puts it a front. Didn't use append since pop returns final element of list,
        # so adding to queue from the front makes it easier

    def dequeue(self):
        return self.nums.pop()



def server_predict(window, player, num_games=1, logged_in=False):
    predictions = {}
    f = open(f'user_score{player}.txt', 'w')  # multiple players?
    f.write('')  # to clear the file, since a new user is now playing, so it will need to be cleared
    f.close()
    n = Network()
    prompts = n.send(('prompts?', 'prompts?'))
    for game_num in range(num_games):

        prompt = prompts.refresh()

        draw(window, prompt, game_num)
        name = f'drawing{game_num}.png'
        d = drawing(prompt, game_num, name)

        perc_certain, guess = n.send((d, 'p'))

        print(f"I'm {perc_certain}% sure that that's a {guess} ")

        predictions[str(game_num + 1)] = str(prompt) + ' ' + str(guess) + ' ' + str(perc_certain)

    f = open(f'user_score{player}.txt', 'a')  # w because rewrite this file for each user. This is just temporary
    for item in predictions.items():
        line = ' '.join(item) + '\n'  # key + value assigned to that key in dictionary, ie number and
        # percentage certainty
        # print(line)
        f.write(line)
    f.close()



def my_predict(window, num_games=1, logged_in=False):
    predictions = {}
    f = open('user_score.txt', 'w')
    f.write('')  # to clear the file, since a new user is now playing, so it will need to be cleared
    f.close()
    x_train, x_test, y_test, y_train = load_dataset()
    x_train, x_test = x_train.T, x_test.T
    prompts = queue(10)
    my_nn = NeuralNetwork(load=True)

    for game_num in range(0, num_games):  # how many times game will be played
        prompt = prompts.refresh()

        d = drawing(prompt, game_num, window)

        x = np.array(prepare_img(f'drawing{game_num}.png'))

        prediction = my_nn.predict(x)
        print(prediction)

        guess = np.argmax(prediction)  # gets largest value from guesses, returns index
        perc_certain = int(round(max(prediction) * 100))

        predictions[str(game_num + 1)] = str(prompt) + ' ' + str(guess) + ' ' + str(perc_certain)
        # adds to dictionary their attempt number(key),prompt, network guess, networks certainty

        print(f"I'm {round(max(prediction) * 100, 2)}% sure that that's a {np.argmax(prediction)} ")
        # rounds it to 2 decimal places

    f = open('user_score.txt', 'a')  # w because rewrite this file for each user. This is just temporary
    for item in predictions.items():
        line = ' '.join(item) + '\n'  # key + value assigned to that key in dictionary, ie number and
        # percentage certainty
        # print(line)
        f.write(line)
    f.close()
