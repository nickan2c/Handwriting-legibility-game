import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()  # loading in database using tensorflow
x_train, x_test = x_train / 255.0, x_test / 255.0

# print(x_train[0], x_train[0].shape)
# plt.imshow(x_train[5], cmap='gray')
# plt.show()




