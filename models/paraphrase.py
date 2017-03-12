import random
import numpy as np
from keras.models import Model
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers.core import *
from keras.layers import Input,merge
from keras.optimizers import SGD, RMSprop
from keras import backend as K


def euclidean_distance(inputs):
    if (len(inputs) != 2):
        raise 'oops'
    output = K.mean(K.square(inputs[0] - inputs[1]), axis=-1)
    output = K.sqrt(output)
    output = K.expand_dims(output, 1)
    return output


def contrastive_loss(y, d):
    """ Contrastive loss from Hadsell-et-al.'06
        http://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf
    """
    margin = 1
    return K.mean(y * K.square(d) + (1 - y) * K.square(K.maximum(margin - d, 0)))


def compute_accuracy(predictions, labels, threshold=0.5):
    """ Compute classification accuracy with a fixed threshold on distances.
    """
    yhat = predictions < threshold
    accuracy = (yhat==labels)
    return accuracy.mean()



class SiameseParaphrase():
    """Simple feedforward paraphrase classification model"""

    def __init__(self, autoencoder, input_dimension):

        # Get the inputs to the autoencoder
        inputLeft = autoencoder.inputs[0]
        inputRight = autoencoder.inputs[1]

        # Get the outputs from the autoencoder
        outputLeft = autoencoder.midpoints[0]
        outputRight = autoencoder.midpoints[1]

        # merge outputs of the base network and compute euclidean distance
        lambda_merge = merge([outputLeft, outputRight], mode=euclidean_distance, output_shape=[[None,1]])

        # create main network
        model = Model([inputLeft,inputRight],lambda_merge)

        # compile
        rms = RMSprop()
        model.compile(loss=contrastive_loss, optimizer=rms)

        # save
        self.autoencoder = autoencoder
        self.model = model

    def fit(self,train_left,train_right,labels):
        """Fit the model to the data"""
        print "Fitting Paraphrase <SiameseParaphrase> model: "
        self.model.fit([train_left, train_right], labels, batch_size=128, nb_epoch=4)

    def evaluate(self, x_left, x_right, labels):
        # compute final accuracy on training and test sets
        pred = self.model.predict([x_left, x_right])
        print pred.shape
        p,r,f,_ = precision_recall_fscore_support(labels, pred, average='binary')
        print('* Accuracy (0.4): %0.2f%%' % (100 * compute_accuracy(pred, labels, 0.4)))
        print('* Accuracy (0.5): %0.2f%%' % (100 * compute_accuracy(pred, labels, 0.5)))
        print('* Accuracy (0.6): %0.2f%%' % (100 * compute_accuracy(pred, labels, 0.6)))



