from pathlib import Path
from typing import Optional

import numpy as np

import matplotlib.pyplot as plt
import tensorflow_datasets as tfds
import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.callbacks import History

tfds.disable_progress_bar()


class IntentClassifier:
    def __init__(self):
        self.model: Optional[Model] = None
        self.history: Optional[History] = None

    def build_rnn_model(self, encoder):
        self.model = tf.keras.Sequential([
            encoder,
            tf.keras.layers.Embedding(len(encoder.get_vocabulary()), 64),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64, return_sequences=True)),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(1)
        ])

        self.model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                                       optimizer=tf.keras.optimizers.Adam(1e-4),
                                       metrics=['accuracy'])

    def save(self, model_path: Path):
        self.model.save(model_path, save_format='tf')

    def load(self, model_path: Path):
        self.model = tf.keras.models.load_model(model_path)

    def train(self):
        dataset, info = tfds.load('imdb_reviews', with_info=True,
                                  as_supervised=True)

        buffer_size = 10000
        batch_size = 64

        train_dataset, test_dataset = dataset['train'], dataset['test']
        train_dataset = train_dataset.shuffle(buffer_size).batch(batch_size).prefetch(tf.data.AUTOTUNE)
        test_dataset = test_dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)

        vocab_size = 1000

        encoder = tf.keras.layers.TextVectorization(max_tokens=vocab_size)
        encoder.adapt(train_dataset.map(lambda text, label: text))

        self.build_rnn_model(encoder)

        self.history = self.model.fit(train_dataset, epochs=10,
                            validation_data=test_dataset,
                            validation_steps=30)

    def infer(self, input_text: str) -> float:
        return self.model.predict(np.array([input_text]))[0][0]

    def plot_graphs(self, metric):
        plt.plot(self.history.history[metric])
        plt.plot(self.history.history['val_'+metric], '')
        plt.xlabel("Epochs")
        plt.ylabel(metric)
        plt.legend([metric, 'val_'+metric])
