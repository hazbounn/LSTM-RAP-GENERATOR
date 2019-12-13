from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation, Embedding, TimeDistributed
from keras.layers import LSTM
from keras.utils import plot_model, to_categorical
import numpy as np
import re
import json


def package_for_training(elements, preprocessed_text, sequence_length, step, OHE_inputs=True):
    # build conversion dictionaries and encode text
    element_to_id = dict((c, i) for i, c in enumerate(elements))
    id_to_element = dict((i, c) for i, c in enumerate(elements))
    encoded_text = [element_to_id[element] for element in preprocessed_text if element in element_to_id]
    del preprocessed_text
    # build sequences and expected outputs
    sequences = []
    next_elements = []
    for i in range(0, len(encoded_text) - sequence_length - 1, step):
        sequences.append(encoded_text[i: i + sequence_length])
        next_elements.append(encoded_text[i + 1: i + sequence_length + 1])

    # convert to one-hot representation for training
    vocabulary_size = len(elements)
    if OHE_inputs:
        x = np.zeros((len(sequences), sequence_length, vocabulary_size), dtype=np.bool)
        y = np.zeros((len(sequences), sequence_length, vocabulary_size), dtype=np.bool)
    else:
        x = np.zeros((len(sequences), sequence_length), dtype=np.int)
        y = np.zeros((len(sequences), sequence_length, 1), dtype=np.int)
    for i, sequence in enumerate(sequences):
        if OHE_inputs:
            x[i, :, :] = to_categorical(sequence, num_classes=vocabulary_size)
            y[i, :, :] = to_categorical(next_elements[i], num_classes=vocabulary_size)
        else:
            x[i, :] = sequence
            for j, e in enumerate(next_elements[i]):
                y[i, j] = [e]

    return x, y, vocabulary_size, id_to_element, element_to_id


# Converts characters to one-hot representation, splitting text into sequences with a step offset
# returns inputs, expected outputs, and a dictionary to convert OHE indices to chars
def generate_char_training_set(text, sequence_length=50, step=3):
    # convert to lowercase, then convert to set of sorted unique characters
    preprocessed_text = text.lower()
    chars = sorted(list(set(preprocessed_text)))
    return package_for_training(chars, preprocessed_text, sequence_length, step)


# Converts words to one-hot representation, splitting text into sequences with a step offset
# returns inputs, expected outputs, and a dictionary to convert OHE indices to words
def generate_word_training_set(text, sequence_length=50, step=3):
    # remove all punctuation and convert to lowercase, then convert to set of sorted unique words
    preprocessed_text = re.sub("[^\w]", " ", text.lower()).split()
    words = sorted(list(set(preprocessed_text)))
    return package_for_training(words, preprocessed_text, sequence_length, step, OHE_inputs=False)


class CharBasedModel:
    # sequence_length: the number time steps per sequence
    # vocabulary_size: the number of characters in the vocabulary
    # hidden_layers: list of hidden layers, in array of int format (ex: [150, 150] for two hidden layers of 150 units)
    def __init__(self, sequence_length=50, vocabulary_size=20, hidden_layers=None):
        self.sequence_length = sequence_length
        self.vocabulary_size = vocabulary_size
        if hidden_layers is None:
            hidden_layers = [150]
        self.model = Sequential()
        self.model.add(LSTM(hidden_layers[0], input_shape=(sequence_length, vocabulary_size), return_sequences=True))
        for layer in hidden_layers[1:]:
            self.model.add(LSTM(layer, return_sequences=True))
        self.model.add(TimeDistributed(Dense(vocabulary_size)))
        self.model.add(Activation('softmax'))
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
        plot_model(self.model, to_file='model.png', show_shapes=True)

    def train(self, x, y, epochs, batch_size):
        self.model.fit(x, y, batch_size=batch_size, epochs=epochs, verbose=1)

    def save(self, filename='charmodel.h5'):
        self.model.save(filename)

    def load(self, filename='charmodel.h5'):
        self.model = load_model(filename)

    def generate(self, seed, length, id_to_element, element_to_id):
        text = seed
        sentence = text
        for i in range(length):
            t = [element_to_id[element] for element in sentence if element in element_to_id]

            sequences = []
            for j in range(0, len(t) - self.sequence_length, 2):
                sequences.append(t[j: j + self.sequence_length])

            x = np.zeros((len(sequences), self.sequence_length, vocabulary_size), dtype=np.bool)
            for j, sequence in enumerate(sequences):
                x[j, :, :] = to_categorical(sequence, num_classes=self.vocabulary_size)

            encoded_text = x

            output_tokens = self.model.predict(encoded_text)
            char = np.argmax(output_tokens[0][-1])
            text += id_to_element[char]
            print(id_to_element[char], end='')
            sentence = sentence[1:] + id_to_element[char]
        return text


# source: https://adventuresinmachinelearning.com/keras-lstm-tutorial/
class WordBasedModel:
    # sequence_length: the number time steps per sequence
    # vocabulary_size: the number of characters in the vocabulary
    # hidden_layers: list of hidden layers, in array of int format (ex: [150, 150] for two hidden layers of 150 units)
    def __init__(self, sequence_length=50, vocabulary_size=20, hidden_layers=None):
        self.sequence_length = sequence_length
        self.vocabulary_size = vocabulary_size
        if hidden_layers is None:
            hidden_layers = [150]
        self.model = Sequential()
        self.model.add(Embedding(vocabulary_size, hidden_layers[0], input_length=sequence_length))
        self.model.add(LSTM(hidden_layers[0], input_shape=(sequence_length, vocabulary_size), return_sequences=True))
        for layer in hidden_layers[1:]:
            self.model.add(LSTM(layer, return_sequences=True))
        self.model.add(TimeDistributed(Dense(vocabulary_size)))
        self.model.add(Activation('softmax'))
        self.model.compile(loss='sparse_categorical_crossentropy', optimizer='adam',
                           metrics=['sparse_categorical_accuracy'])
        plot_model(self.model, to_file='model.png', show_shapes=True)

    def train(self, x, y, epochs, batch_size):
        self.model.fit(x, y, batch_size=batch_size, epochs=epochs, verbose=1)

    def save(self, filename='wordmodel.h5'):
        self.model.save(filename)

    def load(self, filename='wordmodel.h5'):
        self.model = load_model(filename)

    def generate(self, seed, length, id_to_element, element_to_id):
        text = re.sub("[^\w]", " ", seed.lower()).split()
        sentence = text
        for i in range(length):
            t = [element_to_id[element] for element in sentence if element in element_to_id]

            sequences = []
            for j in range(0, len(t) - self.sequence_length, 2):
                sequences.append(t[j: j + self.sequence_length])

            x = np.zeros((len(sequences), self.sequence_length), dtype=np.int)
            for j, sequence in enumerate(sequences):
                x[j, :] = sequence

            encoded_text = x

            output_tokens = self.model.predict(encoded_text)
            char = np.argmax(output_tokens[0][-1])
            # char = np.argmax(output_tokens[0][:, self.sequence_length - 1, :])
            if id_to_element[char] == "endline":
                text += "\n"
                print()
            else:
                text += id_to_element[char] + " "
                print(id_to_element[char] + " ", end='')

            sentence = sentence[1:] + [id_to_element[char]]
        return text


if __name__ == "__main__":
    # this is an example with a single verse to prove functionality.
    # The network is trained and replicates the verse it learned.
    # song: https://genius.com/Yasiin-bey-a-brighter-day-lyrics

    sequence_length = 30

    # char based
    text = "Yo, I speak in whole beat legends \n Divide it up in parts and sections \n Days I was " \
           "ministerin' sectors \n Direct from the spot, forgotten on your election \n Jail laced with " \
           "fragments, speech clipped with accents \n Phenomenal ave and for future and the past tense" \
           " \n Blew up the room in my absence \n Live or closed caption watch my song vibrate with passion" \
           " \n The response in action to light bulb irrations \n I come from where anything can happen " \
           "and usually does \n You find tension where it used to be love \n "
    x, y, vocabulary_size, id_to_element, element_to_id = \
        generate_char_training_set(text, sequence_length=sequence_length, step=1)

    ex = CharBasedModel(sequence_length, vocabulary_size, [500, 500])
    print("start character based training: ")
    ex.train(x, y, 50, 20)

    # word based
    text = "Yo, I speak in whole beat legends<endline>Divide it up in parts and sections<endline>Days I was " \
           "ministerin' sectors<endline>Direct from the spot, forgotten on your election<endline>Jail laced with " \
           "fragments, speech clipped with accents<endline>Phenomenal ave and for future and the past tense<endline>" \
           "Blew up the room in my absence<endline>Live or closed caption watch my song vibrate with passion<endline>" \
           "The response in action to light bulb irrations<endline>I come from where anything can happen and usually" \
           " does<endline>You find tension where it used to be love<endline>"

    x, y, vocabulary_size, id_to_element, element_to_id = \
        generate_word_training_set(text, sequence_length=sequence_length, step=1)

    ex = WordBasedModel(sequence_length, vocabulary_size, [500, 500])
    print("start word based training: ")
    ex.train(x, y, 100, 20)

    print("start character based generation: ")
    ex.generate(text, 150, id_to_element, element_to_id)
    print("\n\n\nstart word based generation: ")
    ex.generate(text, 90, id_to_element, element_to_id)
