import os
import numpy as np
import tensorflow as tf
import h5py
import math

from keras.layers import Layer

class BatchNormalization(Layer):
    # Code from: https://github.com/dksakkos/BatchNorm
    def __init__(self, 
                 axis=-1, 
                 momentum=0.90, 
                 name=None, 
                 synchronized=False,
                 **kwargs):
        super().__init__(name=name, **kwargs)
        self.axis = axis
        self.momentum = momentum 
        #super(BatchNormalization, self).__init__()

    def build(self, input_shape):
        self.beta = self.add_weight(
            name="beta",
            shape=(input_shape[self.axis]),
            initializer="zeros",
            trainable=True,
        )

        self.gamma = self.add_weight(
            name="gamma",
            shape=(input_shape[self.axis]),
            initializer="ones",
            trainable=True,
        )

        self.moving_mean = self.add_weight(
            name="moving_mean",
            shape=(input_shape[self.axis]),
            initializer=tf.initializers.zeros,
            trainable=False)

        self.moving_variance = self.add_weight(
            name="moving_variance",
            shape=(input_shape[self.axis]),
            initializer=tf.initializers.ones,
            trainable=False)

    def get_moving_average(self, statistic, new_value):
        momentum = self.momentum
        new_value = statistic * momentum + new_value * (1 - momentum)
        return statistic.assign(new_value)

    def normalise(self, x, x_mean, x_var):
        return (x - x_mean) / tf.sqrt(x_var + 1e-6)

    def call(self, inputs, training):
        if training:
            assert len(inputs.shape) in (2, 4)
            if len(inputs.shape) > 2:
                axes = [0, 1, 2]
            else:
                axes = [0]
            mean, var = tf.nn.moments(inputs, axes=axes, keepdims=False)
            self.moving_mean.assign(self.get_moving_average(self.moving_mean, mean))
            self.moving_variance.assign(self.get_moving_average(self.moving_variance, var))
        else:
            mean, var = self.moving_mean, self.moving_variance
        x = self.normalise(inputs, mean, var)
        return self.gamma * x + self.beta


def load_dataset():
    train_dataset = h5py.File('datasets/train_signs.h5', "r")
    
    train_set_x_orig = np.array(train_dataset["train_set_x"][:])
    train_set_y_orig = np.array(
        train_dataset["train_set_y"][:])  

    test_dataset = h5py.File('datasets/test_signs.h5', "r")
    
    test_set_x_orig = np.array(test_dataset["test_set_x"][:])
    test_set_y_orig = np.array(
        test_dataset["test_set_y"][:])  

    classes = np.array(test_dataset["list_classes"][:])  

    train_set_y_orig = train_set_y_orig.reshape((1, train_set_y_orig.shape[0]))
    test_set_y_orig = test_set_y_orig.reshape((1, test_set_y_orig.shape[0]))

    return train_set_x_orig, train_set_y_orig, test_set_x_orig, test_set_y_orig, classes


