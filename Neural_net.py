import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

mnist = tf.keras.datasets.mnist
(training_data, training_labels), (test_data, test_labels) = mnist.load_data()  # loads in the mnist dataset
training_data, test_data = training_data / 255, test_data / 255  # normalises mnist colours to between 0 and 1

class Network:
    def __init__(self, sizes, epochs=10, learning_rate=0.01):
        self.sizes = sizes
        self.num_layers = len(sizes)
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]] # each node to node connection has a bias, so the shape is the number of neurons(y), 1. 
        self.epochs = epochs
        self.learning_rate = learning_rate

        self.weights = self.initialization()

    def initialization(self):
        # number of nodes in each layer
        input_layer = self.sizes[0]
        hidden_l1 = self.sizes[1]
        hidden_l2 = self.sizes[2]
        output_layer = self.sizes[3]

        params = {
            'Weights_1': np.random.randn(hidden_l1, input_layer), 
            'Weights_2': np.random.randn(hidden_l2, hidden_l1),
            'Weights_3': np.random.randn(output_layer, hidden_l2)
        } # dictionary to store all parameters. this way I can edit and access parameters more easily

        return params


    def relu(self, x):
        # applying the ReLu activation function
        return np.maximum(0, x)


nn = Network([10, 5, 2, 1])



