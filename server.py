# importing inbuilt libraries
import socket
from _thread import *
import pickle
import random
from tkinter import *
# Importing external libraries
import numpy as np
from PIL import Image, ImageFilter
import tensorflow as tf
# Importing my files
import nn_3

server = "192.168.1.164"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")


class drawing:  # have to redefine class here so that it can unpickle it using the class.
    def __init__(self, prompt, game_num, name='drawing0.png'):
        self.prompt = prompt
        self.game_num = game_num
        self.drawn = None
        self.correct = False
        self.certainty = 0
        self.mnist = np.array(self.prepare(name))

    @staticmethod
    def prepare(image):
        im = Image.open(image).convert('L')  # opens the image in greyscale format, black and white
        new_image = Image.new('L', (28, 28), 255)  # creates white canvas of 28x28 pixels, for later use

        img = im.resize((20, 20), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)  # resizes the image to make it 20x20,
        # as per the mnist dataset standard. smoothens and sharpens image

        h_pos = 4  # horizontal position. original width - new width /2 (so that it can be centered)
        #  or in other words (28 - 20) / 2
        v_pos = 4

        new_image.paste(img, (v_pos, h_pos))  # puts this image on top of the white canvas created earlier
        pixel_values = list(new_image.getdata())

        normalised_values = [(255 - val) / 255.0 for val in pixel_values]  # 255 - x inverts the colour,
        # /255 normalises it to be between 0 and 1
        return np.array(normalised_values)


def all_same(items):
    return all(x == items[0] for x in items)


def predict(x, net):
    if all_same(x):  # if every pixel in the image is the same color, the user hasn't drawn anything, so don't guess
        guess = None
        perc_certain = None
        return perc_certain, guess

    if net == 'cnn':
        loaded_model = tf.keras.models.load_model('cnn.h5')
        reshaped_img = x.reshape(1, 28, 28, 1)  # input for convolutional neural network is shaped like this

        prediction = loaded_model.predict(reshaped_img)
        guess = np.argmax(prediction)
        perc_certain = int(round(max(prediction[0]) * 100, 2))

        return perc_certain, guess

    nn = nn_3.NeuralNetwork(load=True)

    prediction = nn.predict(x)
    guess = np.argmax(prediction)  # finds largest value from guesses, returns index
    perc_certain = int(round(max(prediction) * 100, 2))  # int to get rid of decimal, round to round it

    return perc_certain, guess


def write_predictions(predictions, user):
    f = open(f'user_score{user}.txt', 'a')
    for item in predictions.items():
        line = ' '.join(
            item) + '\n'  # key + value assigned to that key in dictionary, ie number and percentage certainty
        f.write(line)
    f.close()


class queue:  # used to select a prompt, and make sure the prompt isn't the same twice in a row
    def __init__(self, length):
        self.nums = []
        for i in range(0, length):
            self.nums.append(i)
        random.shuffle(self.nums)

    def refresh(self):
        last = self.dequeue()
        self.enqueue(last)
        return last

    def enqueue(self, item):
        self.nums.insert(0, item)

    def dequeue(self):
        return self.nums.pop()


prompts = queue(10)
users = []
num_games = 0
selected_games = False
finished = []
network = ''


def threaded_client(conn):
    # global variables that are needed because they will need to be accessed by both clients.
    global num_games
    global selected_games
    global prompts
    global finished
    global network

    conn.send(pickle.dumps('Connected to NN'))
    reply = ''
    while True:
        try:
            data = pickle.loads(conn.recv(2048 * 4))  # tuple containing data and instruction.

            if not data:
                print("Disconnected")
                break
            else:
                if data[1] == 'Smarter network (easier)':
                    reply = predict(data[0].mnist, 'cnn')
                    finished.append(' ')

                if data[1] == 'Smart network (harder)':
                    reply = predict(data[0].mnist, 'my_nn')
                    finished.append(' ')

                if data[1] == 'init':
                    users.append(data[0])

                if data[1] == 'game':
                    reply = users

                if data[1] == 'num_games':
                    num_games = data[0]
                    selected_games = True

                if data[1] == 'num_games?':
                    reply = num_games

                if data[1] == 'selected?':
                    if selected_games:
                        reply = 'yes'

                if data[1] == 'prompts?':
                    reply = prompts
                    if data[0] == 1:
                        prompts.refresh()

                if data[1] == 'ready?':
                    if len(finished) / num_games == 2:
                        reply = 'yes'

                if data[1] == 'predictions1' or data[1] == 'predictions2':
                    predictions = data[0]
                    user = data[1][-1]
                    write_predictions(predictions, user)

                if data[1] == 'predictions?':
                    f = open(f'user_score{data[0]}.txt', 'r')
                    new_rows = []
                    for row in f:
                        new_row = row[:-1]  # remove \n by list slicing
                        new_rows.append(new_row)

                    reply = new_rows  # sends contents of file back as an array

                if data[1] == 'network':
                    network = data[0]

                if data[1] == 'network?':
                    reply = network

                if data[1] == 'unsend':
                    users.remove(data[0])


            conn.sendall(pickle.dumps(reply))

        except EOFError as e:
            print(e)
            break
    print("Lost connection")
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    start_new_thread(threaded_client, (conn,))
