# NNea
My handwriting recogniser and legibility scorer python program.


Run cnn training model.py first, to create the network. It will require a few minutes to train, then once trained will not be trained again.
If you would like to use the ANN, you can change this in draw_window.py where it loads 'cnn2.h5' to 'mnist.h5', however the default is cnn for now

Then run tkinter_windows.py for the gui. this imports draw_window so no need to open that

Modules used:

Internal:
tkinter,
sqlite3,
hashlib

External:
Tensorflow,
PIL / pillow,
numpy

