import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

mnist = tf.keras.datasets.mnist
(training_data, training_labels), (test_data, test_labels) = mnist.load_data()  # loads in the mnist dataset
training_data, test_data = training_data / 255, test_data / 255  # normalises mnist colours to between 0 and 1

print(training_data[0], training_data[0].shape)
plt.imshow(training_data[5], cmap='gray')
plt.show()


