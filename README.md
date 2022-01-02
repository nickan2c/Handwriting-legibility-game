# NNea
My handwriting recogniser and legibility scorer python program.

Uses my own neural network created only with numpy, which can recognise and score handwriting from a scale of 0 to 100, based on how similar it is to the MNIST database. I have included the tensorflow models which i have based this off of. 

Players can also play online, with another player where they compete to see who has the neatest handwriting.

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

