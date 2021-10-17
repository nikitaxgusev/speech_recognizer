from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
import queue
import threading
import sys
import sounddevice as sd
import soundfile as sf


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # setting title
        self.setWindowTitle("Speech recognizer")

        # setting geometry
        self.setGeometry(100, 100, 600, 120)

        # calling method
        self.UiComponents()

        # showing all the widgets
        self.show()

    # method for widgets
    def UiComponents(self):
        # Buttons:
        self.button_start_stop_record = QPushButton("Start record", self)
        self.button_start_stop_record.setGeometry(0, 90, 70, 30)
        self.button_start_stop_record.clicked.connect(self.handle_start_stop_record_button)

        self.button_play_record = QPushButton("Play record", self)
        self.button_play_record.setGeometry(70, 90, 70, 30)
        self.button_play_record.setEnabled(False)
        self.button_play_record.clicked.connect(self.handle_play_record_button)

        self.button_recognize_to_text = QPushButton("Recognize to text", self)
        self.button_recognize_to_text.setGeometry(140, 90, 100, 30)
        self.button_recognize_to_text.setEnabled(False)
        self.button_recognize_to_text.clicked.connect(self.handle_recognize_to_text_button)

        self.button_classification_text = QPushButton("Classification the text", self)
        self.button_classification_text.setGeometry(240, 90, 120, 30)
        self.button_classification_text.setEnabled(False)
        self.button_classification_text.clicked.connect(self.handle_classification_text_button)

        self.button_generate_answer = QPushButton("Generate the answer", self)
        self.button_generate_answer.setGeometry(360, 90, 120, 30)
        self.button_generate_answer.setEnabled(False)
        self.button_generate_answer.clicked.connect(self.handle_generate_answer_button)

        # Labels:
        self.label_title_words_from_rec = QLabel("Text from voice:", self)
        self.label_title_words_from_rec.setGeometry(0, 2, 140, 20)
        self.label_title_words_from_rec.setFont(QFont('Arial', 15))

        self.label_words_from_rec = QLabel(self)
        self.label_words_from_rec.setGeometry(142, 2, 458, 20)
        self.label_words_from_rec.setFont(QFont('Arial', 15))

        self.label_title_classification = QLabel("Classification:", self)
        self.label_title_classification.setGeometry(0, 30, 119, 20)
        self.label_title_classification.setFont(QFont('Arial', 15))

        self.label_classification = QLabel(self)
        self.label_classification.setGeometry(124, 30, 476, 20)
        self.label_classification.setFont(QFont('Arial', 15))

        self.label_title_answer = QLabel("Answer:", self)
        self.label_title_answer.setGeometry(0, 60, 70, 20)
        self.label_title_answer.setFont(QFont('Arial', 15))

        self.label_answer = QLabel(self)
        self.label_answer.setGeometry(75, 60, 525, 20)
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

    def get_filename(self):
        return self.filename

    def set_buttons(self, enable):
        self.button_play_record.setEnabled(enable)
        self.button_recognize_to_text.setEnabled(enable)
        self.button_classification_text.setEnabled(enable)
        self.button_generate_answer.setEnabled(enable)

    def clear_labels(self):
        self.label_words_from_rec.setText("")
        self.label_classification.setText("")
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
    def handle_classification_text_button(self):
        # TODO: add getting classification and remove line below
        self.label_classification.setText("1, 2, 3, 4")

    @pyqtSlot()
    def handle_recognize_to_text_button(self):
        # TODO: add getting speech_recognizer::from_speech_to_text and remove line below
        self.label_words_from_rec.setText("Bla bla bla")

    @pyqtSlot()
    def handle_generate_answer_button(self):
        # TODO: add getting answer and remove line below
        self.label_answer.setText("Answer")

    filename = "record.wav"
    subtype = 'PCM_16'
    dtype = 'int16'
    q = queue.Queue()
    recorder = False


# TODO: from test only. After test remove lines below
if __name__ == "__main__":
    App = QApplication([])
    window = Window()
    sys.exit(App.exec())
