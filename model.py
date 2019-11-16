from keras.callbacks import ModelCheckpoint
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.utils import plot_model
import numpy as np
import collections


# Source: https://github.com/kjaisingh/rap-lyrics-generator/blob/master/train.py
def generate_char_training_set(text, sequence_length=50, step=3):
    chars = sorted(list(set(text)))
    char_to_indices = dict((c, i) for i, c in enumerate(chars))
    indices_to_char = dict((i, c) for i, c in enumerate(chars))

    sentences = []
    next_chars = []
    for i in range(0, len(text) - sequence_length, step):
        sentences.append(text[i: i + sequence_length])
        next_chars.append(text[i + sequence_length])

    x = np.zeros((len(sentences), sequence_length, len(chars)), dtype=np.bool)
    y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
    for i, sentence in enumerate(sentences):
        for t, char in enumerate(sentence):
            x[i, t, char_to_indices[char]] = 1
        y[i, char_to_indices[next_chars[i]]] = 1

    return x, y, indices_to_char


class CharBasedModel:
    # sequence_length: the number time steps per sequence
    # vocabulary_size: the number of characters in the vocabulary
    # hidden_layers: list of hidden layers, in array of int format (ex: [150, 150] for two hidden layers of 150 units)
    def __init__(self, sequence_length=50, vocabulary_size=20, hidden_layers=None):
        if hidden_layers is None:
            hidden_layers = [150]
        self.model = Sequential()
        self.model.add(LSTM(hidden_layers[0], input_shape=(sequence_length, vocabulary_size), return_sequences=True))
        for layer in hidden_layers[1:]:
            self.model.add(LSTM(layer, return_sequences=True))
        self.model.add(Dense(vocabulary_size))
        self.model.add(Activation('softmax'))
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
        plot_model(self.model, to_file='model.png', show_shapes=True)

    def train(self, x, y, epochs, batch_size):

        self.model.fit(x, y, batch_size=batch_size, epochs=epochs,
                       callbacks=ModelCheckpoint(filepath='./model-{epoch:02d}.h5', verbose=1))

    def save(self, filename='charmodel.h5'):
        self.model.save(filename)

    def load(self, filename='charmodel.h5'):
        self.model = load_model(filename)


def generate_word_training_set(text, sequence_length=50, step=3):
    counter = collections.Counter(text)
    count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))

    words, _ = list(zip(*count_pairs))
    word_to_id = dict(zip(words, range(len(words))))

    encoded_text = [word_to_id[word] for word in text if word in word_to_id]


# source: https://adventuresinmachinelearning.com/keras-lstm-tutorial/
class WordBasedModel:
    # sequence_length: the number time steps per sequence
    # vocabulary_size: the number of characters in the vocabulary
    # hidden_layers: list of hidden layers, in array of int format (ex: [150, 150] for two hidden layers of 150 units)
    def __init__(self, sequence_length=50, vocabulary_size=20, hidden_layers=None):
        if hidden_layers is None:
            hidden_layers = [150]
        self.model = Sequential()
        self.model.add(LSTM(hidden_layers[0], input_shape=(sequence_length, vocabulary_size), return_sequences=True))
        for layer in hidden_layers[1:]:
            self.model.add(LSTM(layer, return_sequences=True))
        self.model.add(Dense(vocabulary_size))
        self.model.add(Activation('softmax'))
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
        plot_model(self.model, to_file='model.png', show_shapes=True)

    def train(self, x, y, epochs, batch_size, text):
        self.model.fit(x, y, batch_size=batch_size, epochs=epochs,
                       callbacks=ModelCheckpoint(filepath='./model-{epoch:02d}.h5', verbose=1))

    def save(self, filename='charmodel.h5'):
        self.model.save(filename)

    def load(self, filename='charmodel.h5'):
        self.model = load_model(filename)


ex = CharBasedModel(20, 20, [500, 500])
