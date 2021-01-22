import socket
from _thread import *
import pickle
from tkinter import *
import tensorflow as tf
import numpy as np
from PIL import Image, ImageFilter
import my_nn

server = "192.168.1.103"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")


# loaded_model = tf.keras.models.load_model('cnn2.h5')

class drawing:  # have to redefine class here so that it can unpickle it using the class.
    def __init__(self, prompt, game_num, name='drawing0.png'):
        self.prompt = prompt
        self.game_num = game_num
        self.drawn = None
        self.correct = False
        self.certainty = 0
        self.mnist = np.array(self.prepare(name))
        # print(self.mnist)

    def eval(self, correct, certainty):
        self.correct = correct
        self.certainty = certainty

    def prepare(self, image):
        im = Image.open(image).convert('L')  # opens the image in greyscale format, black and white
        new_image = Image.new('L', (28, 28), 255)  # creates white canvas of 28x28 pixels, for later use

        img = im.resize((20, 20), Image.ANTIALIAS).filter(
            ImageFilter.SHARPEN)  # resizes the image to make it 20x20, as per
        # the mnist dataset standard. Antialias is used to smooth the image out, and sharpen sharpens it
        h_pos = 4  # horizontal position. original width - new width /2 (so that it can be centered)
        #  or in other words (28 - 20) / 2
        v_pos = 4  # vertical position. Same reasoning as horizontal

        new_image.paste(img, (v_pos, h_pos))  # puts this image on top of the white canvas created earlier
        pixel_values = list(new_image.getdata())  # get pixel values

        normalised_values = [(255 - val) / 255.0 for val in pixel_values]  # 255 - x inverts the colour,
        # /255 normalises it to be between 0 and 1
        return np.array(normalised_values)


def predict(x):
    loaded_model = tf.keras.models.load_model('cnn2.h5')
    nn = my_nn.NeuralNetwork(load=True)
    prediction = nn.predict(x)
    guess = np.argmax(prediction)  # finds largest value from guesses, returns index
    perc_certain = int(round(max(prediction) * 100, 2))  # int to get rid of decimal, round to round it

    return perc_certain, guess


def threaded_client(conn):
    drawings = []
    conn.send(pickle.dumps('Connected to NN'))

    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048 * 4))

            if not data:
                print("Disconnected")
                break
            else:
                reply = predict(data.mnist)

                print("Received: ", data)
                print("Sending : ", reply)

            conn.sendall(pickle.dumps(reply))

        except:
            break

    print("Lost connection")
    conn.close()


currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn,))
    currentPlayer += 1
