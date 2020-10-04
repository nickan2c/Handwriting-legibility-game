import numpy as np


class Network:

    def __init__(self, sizes):  # sizes is the amount of neurons in each layer, in the form [x,y,z, ...]
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]  # numpy built in function outputs a random number,from
        # a Gaussian distribution, with mean 0 and standard deviation 1
        # values passed in represent size of vector, eg np.random.randn(3,1) will give a vector [[x],[x],[x]]
        # it is set to 1 because each bias is only for one neuron
        self.weights = [np.random.randn(y, x) for x, y in zip(sizes[:-1], sizes[1:])]  # zip concatenates each value at
        # the same point in two arrays   eg zip([1,3,5], [2,4,6]) would give 1 2, 3 4, 5 6
        # creates a numpy array representing each weighted connection between each layer

    def feedforward(self, inputs): # output of a neuron is w * inputs + b
        for b, w in zip(self.biases, self.weights):
            a = np.dot(w, inputs) + b # np.dot is a multiplication of vectors, since * does not work in this case
            z = sigmoid(a)  # applying sigmoid
        return z


def sigmoid(x):
    # applying the sigmoid activation function
    return 1 / (1 + np.exp(-x))  # e^-x


network = Network([2, 3, 1])
print(network.weights)
