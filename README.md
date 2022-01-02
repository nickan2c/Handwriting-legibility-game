# NNea
My handwriting recogniser and legibility scorer python program.

Uses my own neural network created only with numpy, which can recognise and score handwriting from a scale of 0 to 100, based on how similar it is to the MNIST database. I have included the tensorflow models which i have based this off of.


In the client server branch, players can also play online, with another player where they compete to see who has the neatest handwriting.

Run cnn training model.py first, to create the network. It will require a few minutes to train, then once trained will not be trained again. If you would like to use the ANN, you can change this in draw_window.py where it loads 'cnn2.h5' to 'mnist.h5', however the default is cnn for now

run tkinter_windows.py and the program will run, if the server is running. Must input your IP address into server.py and into network.py for it to run on your machine.


Modules used:

Internal:
tkinter,
sqlite3,
hashlib

External:
Tensorflow,
PIL / pillow,
numpy

