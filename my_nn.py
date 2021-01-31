import tensorflow as tf
import numpy as np

def softmax(x):
    exp_values = np.exp(x - np.max(x))  # subtract to keep numerically stable, as exponential rises very quickly, and
    output = exp_values / np.sum(exp_values, axis=0)  # will make training slow/ give nan numbers
    return output


def sigmoid(x, derivative=False):
    '''
    applying the sigmoid activation function
    :param x:
    :param derivative: if true return sigmoid derivative. Used in backpropagation phase
    '''
    if derivative:
        return sigmoid(x) * (1 - sigmoid(x))
    return 1 / (1 + np.exp(-x))  # e^-x


def cross_entropy_loss(y, y_hat):
    '''
    applies loss function to calculate how different y and y hat are
    :param y: desired outputs
    :param y_hat: output of network
    :return: loss
    '''
    L_sum = np.sum(np.multiply(y, np.log(y_hat)))  # no subtract?
    m = y.shape[1]
    loss = -(1 / m) * L_sum

    return loss


def load_dataset():
    '''
    loads dataset using tensorflow
    :return: training data, test data, training labels, test labels
    '''
    mnist = tf.keras.datasets.mnist  # loading with tensorflow
    (training_data, training_labels), (test_data, test_labels) = mnist.load_data()  # loads in the mnist dataset
    training_data, test_data = training_data / 255, test_data / 255  # normalises mnist colours to between 0 and 1
    training_data, test_data = np.array(training_data), np.array(test_data)  # numpy array useful for reshaping and
    # other things

    flattened_training_data = training_data.reshape(len(training_data), 784)  # changes shape from 28,28 to 784,
    flattened_test_data = test_data.reshape(len(test_data), 784)  # since that is how it will be inputted

    new_training_labels = get_one_hot(training_labels)

    return flattened_training_data, flattened_test_data, test_labels, new_training_labels


def get_one_hot(targets, nb_classes=10):
    '''
        :param targets: integer
        :return: an array with 10 digits, where y is the index.
        for example input 4 will give [0,0,0,0,1,0,0,0,0,0]
        better because can be directly compared with output of network
        https://stackoverflow.com/questions/38592324/one-hot-encoding-using-numpy
    '''
    res = np.eye(nb_classes)[np.array(targets).reshape(-1)]
    return res.reshape(list(targets.shape) + [nb_classes])


class NeuralNetwork:
    def __init__(self, load):

        self.learning_rate = 2
        self.num_train_images = 60000  # num images
        np.random.seed(138)
        self.W1, self.b1, self.W2, self.b2, self.W3, self.b3 = self.initialise(load)

    def initialise(self, load=False):
        if not load:
            # initialise weights and biases in shape of layers
            W1 = np.random.randn(256, 784) * np.sqrt(1. / 256)
            b1 = np.zeros((256, 1))
            W2 = np.random.randn(10, 256) * np.sqrt(1. / 256)
            b2 = np.zeros((10, 1))
            W3 = np.random.randn(10, 128) * np.sqrt(1. / 256)
            b3 = np.zeros((10, 1))
        elif load:
            W1 = np.load('Weight_layers1.npy')
            b1 = np.load('biases1.npy')
            W2 = np.load('Weight_layers2.npy')
            b2 = np.load('biases2.npy')
            W3 = np.load('Weight_layers3.npy')
            b3 = np.load('biases3.npy')

        return W1, b1, W2, b2, W3, b3

    def forward_pass(self, inputs):
        # output of each layer stored so that network can use it in backprop

        self.Z1 = np.matmul(self.W1, inputs) + self.b1
        self.A1 = sigmoid(self.Z1)
        self.Z2 = np.matmul(self.W2, self.A1) + self.b2
        self.A2 = sigmoid(self.Z2)
        self.Z3 = np.matmul(self.W3, self.A2) + self.b3
        self.A3 = np.exp(self.Z3) / np.sum(np.exp(self.Z3), axis=0)

        return self.A3  # value is returned for viewing output

    def backprop(self, inputs, Y):
        d_cost = self.A3 - Y
        d_cost_d_W3 = (1. / self.num_train_images) * np.matmul(d_cost, self.A2.T)
        d_cost_d_b3 = (1. / self.num_train_images) * np.sum(d_cost, axis=1, keepdims=True)

        dA2 = np.matmul(self.W3.T, d_cost)
        dZ2 = dA2 * sigmoid(self.Z2, derivative=True) * (1 - sigmoid(self.Z2, derivative=True))
        d_cost_d_W2 = (1. / self.num_train_images) * np.matmul(dZ2, self.A1.T)
        d_cost_d_b2 = (1. / self.num_train_images) * np.sum(dZ2, axis=1, keepdims=True)

        dA1 = np.matmul(self.W2.T, dZ2)
        dZ1 = dA1 * sigmoid(self.Z1, derivative=True) * (1 - sigmoid(self.Z1, derivative=True))
        d_cost_d_W1 = (1. / self.num_train_images) * np.matmul(dZ1, inputs.T)
        d_cost_d_b1 = (1. / self.num_train_images) * np.sum(dZ1, axis=1, keepdims=True)

        return d_cost_d_W3, d_cost_d_b3,d_cost_d_W2, d_cost_d_b2, d_cost_d_W1, d_cost_d_b1

    def update_parameters(self,d_cost_d_W3, d_cost_d_b3, d_cost_d_W2, d_cost_d_b2, d_cost_d_W1, d_cost_d_b1):
        # Stochastic gradient descent optimiser method used to update parameters
        self.W3 = self.W3 - self.learning_rate * d_cost_d_W3
        self.b3 = self.b3 - self.learning_rate * d_cost_d_b3
        self.W2 = self.W2 - self.learning_rate * d_cost_d_W2
        self.b2 = self.b2 - self.learning_rate * d_cost_d_b2
        self.W1 = self.W1 - self.learning_rate * d_cost_d_W1
        self.b1 = self.b1 - self.learning_rate * d_cost_d_b1

    def train(self, inputs, y_train):
        y_train = y_train.T
        for i in range(300):
            self.forward_pass(inputs)  # get current outputs
            # backpropagate to find derivatives and error
            d_cost_d_W3, d_cost_d_b3, d_cost_d_W2, d_cost_d_b2, d_cost_d_W1, d_cost_d_b1= self.backprop(x_train, y_train)

            # update parameters
            self.update_parameters(d_cost_d_W3, d_cost_d_b3,d_cost_d_W2, d_cost_d_b2, d_cost_d_W1, d_cost_d_b1)

            if i % 10 == 0:  # print training cost every 100 epochs.
                cost = cross_entropy_loss(y_train, self.A3)
                print(f'Epoch {i},cost:{cost}')


    def test(self, x, y):
        self.forward_pass(x)
        correct = 0

        for output, label in zip(self.A3.T, y):
            # print(output, label)
            if np.argmax(output) == label:
                correct += 1

        accuracy = correct / 10000

        return correct, accuracy

    def predict(self, x):
        x = x.reshape(784, 1) # reshape so network can read
        self.forward_pass(x)
        out = []
        for i in self.A3:  # turn it into a list
            out.append(i[0])
        return out


x_train, x_test, y_test, y_train = load_dataset()
x_train, x_test = x_train.T, x_test.T

loadweights = True

nn = NeuralNetwork(loadweights)
#nn.train(x_train, y_train)
print(nn.test(x_test, y_test))

#Uncomment if you want to save the new weights and biases after training
# np.save('Weight_layers1', nn.W1)
# np.save('biases1', nn.b1)
# np.save('Weight_layers2', nn.W2)
# np.save('biases2', nn.b2)
# np.save('Weight_layers3', nn.W3)
# np.save('biases3', nn.b3)
