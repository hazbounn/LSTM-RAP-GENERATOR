from keras.callbacks import ModelCheckpoint
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation, Embedding
from keras.layers import LSTM
from keras.utils import plot_model, to_categorical
import numpy as np
import re


# Source: https://github.com/kjaisingh/rap-lyrics-generator/blob/master/train.py
def package_for_training(elements, preprocessed_text, sequence_length, step):
    # build conversion dictionaries and encode text
    element_to_id = dict((c, i) for i, c in enumerate(elements))
    id_to_element = dict((i, c) for i, c in enumerate(elements))
    encoded_text = [element_to_id[element] for element in preprocessed_text if element in element_to_id]

    # build sequences and expected outputs
    sequences = []
    next_chars = []
    for i in range(0, len(encoded_text) - sequence_length, step):
        sequences.append(encoded_text[i: i + sequence_length])
        next_chars.append(encoded_text[i + sequence_length])

    # convert to one-hot representation for training
    vocabulary_size = len(elements)
    x = np.zeros((len(sequences), sequence_length, vocabulary_size), dtype=np.bool)
    y = np.zeros((len(sequences), vocabulary_size), dtype=np.bool)
    for i, sequence in enumerate(sequences):
        x[i, :, :] = to_categorical(sequence, num_classes=vocabulary_size)
        y[i, :] = to_categorical(next_chars[i], num_classes=vocabulary_size)

    return x, y, vocabulary_size, id_to_element


# Converts characters to one-hot representation, splitting text into sequences with a step offset
# returns inputs, expected outputs, and a dictionary to convert OHE indices to chars
def generate_char_training_set(text, sequence_length=50, step=3):
    # convert to lowercase, then convert to set of sorted unique characters
    preprocessed_text = text.lower()
    chars = sorted(list(set(preprocessed_text)))
    return package_for_training(chars, preprocessed_text, sequence_length, step)


# Converts words to one-hot representation, splitting text into sequences with a step offset
# returns inputs, expected outputs, and a dictionary to convert OHE indices to chars
def generate_word_training_set(text, sequence_length=50, step=3):
    # remove all punctuation and convert to lowercase, then convert to set of sorted unique words
    preprocessed_text = re.sub("[^\w]", " ",  text.lower()).split()
    words = sorted(list(set(preprocessed_text)))
    return package_for_training(words, preprocessed_text, sequence_length, step)


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

    def save(self, filename='wordmodel.h5'):
        self.model.save(filename)

    def load(self, filename='wordmodel.h5'):
        self.model = load_model(filename)


# source: https://adventuresinmachinelearning.com/keras-lstm-tutorial/
class WordBasedModel:
    # sequence_length: the number time steps per sequence
    # vocabulary_size: the number of characters in the vocabulary
    # hidden_layers: list of hidden layers, in array of int format (ex: [150, 150] for two hidden layers of 150 units)
    def __init__(self, sequence_length=50, vocabulary_size=20, hidden_layers=None):
        if hidden_layers is None:
            hidden_layers = [150]
        self.model = Sequential()
        self.model.add(Embedding(vocabulary_size, hidden_layers[0], input_length=sequence_length))
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


if __name__ == "__main__":
    # ex = CharBasedModel(20, 20, [500, 500])
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et " \
           "dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip " \
           "ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu " \
           "fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt "\
           "mollit anim id est laborum."
    generate_word_training_set(text, sequence_length=10, step=2)
