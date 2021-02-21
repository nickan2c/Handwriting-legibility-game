import tensorflow as tf

mnist = tf.keras.datasets.mnist
(training_data, training_labels), (test_data, test_labels) = mnist.load_data()  # loads in the mnist dataset
training_data, test_data = training_data / 255, test_data / 255  # normalises mnist colours to between 0 and 1

flattened_training_data = training_data.reshape(len(training_data), 784)  # changes shape from 28,28 to 784
flattened_test_data = test_data.reshape(len(test_data), 784)

model = tf.keras.Sequential([
    tf.keras.layers.Flatten(input_shape=(784,)),
    tf.keras.layers.Dense(256, activation=tf.nn.relu),
    tf.keras.layers.Dense(256, activation=tf.nn.relu),
    tf.keras.layers.Dense(10, activation=tf.nn.softmax)
])
# creates model. I talk about my decisions for network size/layers in my documents

model.compile(optimizer="SGD",
                loss='sparse_categorical_crossentropy',
                metrics=["accuracy"])
# select optimizer and loss function. Set it to display accuracy while training. More about this in the documentation

model.fit(flattened_training_data, training_labels, epochs=5) # trains the model on the data

model.evaluate(flattened_test_data, test_labels) # tests the model on unsees data to get an accuracy

model.save('trained_model.h5')  # saves structure of model, weights, training configuration
