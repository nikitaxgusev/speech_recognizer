from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
from pygame import mixer
from speech_recognizer import SpeechRecognizer as sr
import queue
import threading
import sounddevice as sd
import soundfile as sf
import os
from intent_classifier.train import IntentClassifier


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.filename = "record.wav"
        self.subtype = 'PCM_16'
        self.dtype = 'int16'
        self.q = queue.Queue()
        self.recorder = False
        self.recognizer = sr(self.filename)

        self.ic = IntentClassifier()
        self.ic.load("train_Data")

        # setting title
        self.setWindowTitle("Speech recognizer")

        # setting geometry
        self.setGeometry(100, 100, 600, 150)

        # calling method
        self.UiComponents()

        # showing all the widgets
        self.show()

    # method for widgets
    def UiComponents(self):
        # Buttons:
        self.button_start_stop_record = QPushButton("Start record", self)
        self.button_start_stop_record.setGeometry(0, 120, 70, 30)
        self.button_start_stop_record.clicked.connect(self.handle_start_stop_record_button)

        self.button_play_record = QPushButton("Play record", self)
        self.button_play_record.setGeometry(70, 120, 70, 30)
        self.button_play_record.setEnabled(False)
        self.button_play_record.clicked.connect(self.handle_play_record_button)

        self.button_recognize_to_text = QPushButton("Recognize to text", self)
        self.button_recognize_to_text.setGeometry(140, 120, 100, 30)
        self.button_recognize_to_text.setEnabled(False)
        self.button_recognize_to_text.clicked.connect(self.handle_recognize_to_text_button)

        self.button_calculate_emotion_of_text = QPushButton("Calculate emotion of text ", self)
        self.button_calculate_emotion_of_text.setGeometry(240, 120, 135, 30)
        self.button_calculate_emotion_of_text.setEnabled(False)
        self.button_calculate_emotion_of_text.clicked.connect(self.handle_calculate_emotion_of_text_button)

        self.button_generate_answer = QPushButton("Generate the answer", self)
        self.button_generate_answer.setGeometry(375, 120, 120, 30)
        self.button_generate_answer.setEnabled(False)
        self.button_generate_answer.clicked.connect(self.handle_generate_answer_button)

        # Labels:
        self.label_title_words_from_rec = QLabel("Text from voice:", self)
        self.label_title_words_from_rec.setGeometry(0, 2, 140, 30)
        self.label_title_words_from_rec.setFont(QFont('Arial', 15))

        self.label_words_from_rec = QLabel(self)
        self.label_words_from_rec.setGeometry(142, 2, 458, 30)
        self.label_words_from_rec.setFont(QFont('Arial', 15))

        self.label_title_coefficient = QLabel("Positivity coefficient:", self)
        self.label_title_coefficient.setGeometry(0, 40, 180, 30)
        self.label_title_coefficient.setFont(QFont('Arial', 15))

        self.label_coefficient = QLabel(self)
        self.label_coefficient.setGeometry(182, 40, 476, 30)
        self.label_coefficient.setFont(QFont('Arial', 15))

        self.label_title_answer = QLabel("Evaluation of the text:", self)
        self.label_title_answer.setGeometry(0, 78, 190, 30)
        self.label_title_answer.setFont(QFont('Arial', 15))

        self.label_answer = QLabel(self)
        self.label_answer.setGeometry(192, 78, 525, 30)
        self.label_answer.setFont(QFont('Arial', 15))

    def rec(self):
        with sf.SoundFile(self.filename, mode='w', samplerate=44100,
                          subtype=self.subtype, channels=1) as file:
            with sd.InputStream(samplerate=44100.0, dtype=self.dtype,
                                channels=1, callback=self.save):
                while getattr(recorder, "record", True):
                    file.write(self.q.get())

    def save(self, indata, frames, time, status):
        self.q.put(indata.copy())

    def start(self):
        global recorder
        recorder = threading.Thread(target=self.rec)
        recorder.record = True
        recorder.start()

    def stop(self):
        global recorder
        recorder.record = False
        recorder.join()
        recorder = False

    def set_buttons(self, enable):
        self.button_play_record.setEnabled(enable)
        self.button_recognize_to_text.setEnabled(enable)
        self.button_calculate_emotion_of_text.setEnabled(enable)
        self.button_generate_answer.setEnabled(enable)

    def clear_labels(self):
        self.label_words_from_rec.setText("")
        self.label_words_from_rec.setToolTip("")
        self.label_coefficient.setText("")
        self.label_answer.setText("")

    # buttons slots
    @pyqtSlot()
    def handle_start_stop_record_button(self):
        text = self.button_start_stop_record.text()
        if text == "Start record":
            self.button_start_stop_record.setText("Stop record")
            self.start()
            self.set_buttons(False)
            self.clear_labels()

        elif text == "Stop record":
            self.button_start_stop_record.setText("Start record")
            self.stop()
            self.set_buttons(True)

    @pyqtSlot()
    def handle_play_record_button(self):
        data, fs = sf.read(self.filename, dtype='float32')
        sd.play(data, fs)
        sd.wait()  # Wait until file is done playing

    @pyqtSlot()
    def handle_calculate_emotion_of_text_button(self):
        if self.label_words_from_rec.toolTip() != "":
            self.label_coefficient.setText(str(self.ic.infer(self.label_words_from_rec.toolTip())))

    @pyqtSlot()
    def handle_recognize_to_text_button(self):
        text = self.recognizer.from_speech_to_text()

        self.label_words_from_rec.setToolTip(text)
        if len(text) > 48:
            text = text[:49] + "..."

        self.label_words_from_rec.setText(text)

    @pyqtSlot()
    def handle_generate_answer_button(self):
        if self.label_coefficient.text() != "":
            if os.path.exists('answer.mp3'):
                os.remove('answer.mp3')

            answer = "negative"
            coefficient = float(self.label_coefficient.text())
            if coefficient > 0.6:
                answer = "positive"
            elif coefficient > 0.2:
                answer = "slightly positive"
            elif coefficient > -0.2:
                answer = "neutral"
            elif coefficient > -0.6:
                answer = "slightly negative"

            self.label_answer.setText(answer)
            self.recognizer.from_text_to_speech("Text is " + answer)

            mixer.init()
            mixer.music.load(self.recognizer.get_answer_filename())
            mixer.music.play()
            while mixer.music.get_busy():
                pass
            mixer.quit()


# TODO: from test only. After tests comment lines below
# if __name__ == "__main__":
#     App = QApplication([])
#     window = Window()
#     sys.exit(App.exec())
