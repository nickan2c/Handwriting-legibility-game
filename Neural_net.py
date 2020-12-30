import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

mnist = tf.keras.datasets.mnist
(training_data, training_labels), (test_data, test_labels) = mnist.load_data()  # loads in the mnist dataset
training_data, test_data = training_data / 255, test_data / 255  # normalises mnist colours to between 0 and 1
training_data, test_data = np.array(training_data), np.array(test_data)
flattened_training_data = training_data.reshape(len(training_data), 784)  # changes shape from 28,28 to 784
flattened_test_data = test_data.reshape(len(test_data), 784)

print(flattened_training_data.shape)


def softmax(x):
    exp_values = np.exp(x - np.max(x))  # subtract to keep numbers low, as exponential rises very quickly, and
    probabilities = exp_values / np.sum(exp_values)  # will make training slow
    return probabilities


def relu(x):
    # applying the ReLu activation function
    return np.maximum(0, x)


def sigmoid(x):
    # applying the sigmoid activation function
    return 1 / (1 + np.exp(-x))  # e^-x


class Network:
    def __init__(self, sizes, epochs=10, learning_rate=0.01):
        self.sizes = sizes
        self.num_layers = len(sizes)

        self.epochs = epochs
        self.learning_rate = learning_rate

        self.params = self.initialization()

    def initialization(self):
        # number of nodes in each layer
        input_layer = self.sizes[0]
        hidden_l1 = self.sizes[1]
        hidden_l2 = self.sizes[2]
        output_layer = self.sizes[3]

        params = {
            'Weights_1': np.random.randn(hidden_l1, input_layer),
            'Weights_2': np.random.randn(hidden_l2, hidden_l1),
            'Weights_3': np.random.randn(output_layer, hidden_l2),
            'bias_1': np.random.randn(hidden_l1),
            'bias_2': np.random.randn(hidden_l2),
            'bias_3': np.random.randn(output_layer)

        }

        return params

    def forward(self, training_inputs):

        self.params['Z1'] = self.feedforward(training_inputs.T, 1)
        print(self.params['Z1'].shape)
        self.params['Z2'] = self.feedforward(self.params['Z1'], 2)
        #
        self.params['Z3'] = self.feedforward(self.params['Z2'], 3, activation_func='softmax')

        return self.params['Z3'].T

    def feedforward(self, a, layer, activation_func='relu'):
        """Return the output of the network when `a` is input."""
        weights = 'Weights_' + str(layer)  # weights_1 would be the first layer, etc
        bias = 'bias_' + str(layer)
        w = self.params[weights]
        b = self.params[bias]
        #print(w.shape)
        if activation_func == 'relu':
            z = np.dot(w, a)+b  # does matrix multiplication of weights by inputs, and then adds bias
            z = sigmoid(z)
        elif activation_func == 'softmax':
            z = (np.dot(w, a)) + b  # does matrix multiplication of weights by inputs, and then# adds bias
            z = softmax(z)

        return z


nn = Network([784, 256, 128, 10])


