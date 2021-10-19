import speech_recognition as sr

from gtts import gTTS

class speech_recognizer:
    def __init__(self, filename):
        self.filename = filename
        self.recognizer = sr.Recognizer()
    # open the file
    def from_speech_to_text(self):
        text = ""
        try:
            with sr.AudioFile(self.filename) as source:
                # listen for the data (load audio to memory)
                audio_data = self.recognizer.record(source)
                # recognize (convert from speech to text)
                text = self.recognizer.recognize_google(audio_data, language='ru-RU')
        finally:
            return text

    def from_text_to_speech(self, text):
        speech = gTTS(text, lang='ru')
        speech.save(self.answer_file)

    def get_answer_filename(self):
        return self.answer_file

    answer_file = "answer.mp3"

# TODO: from test only. After tests remove lines below
# if __name__ == "__main__":
#     filename = "record_1.wav"
#     recognizer = speech_recognizer(filename)
#     text = recognizer.from_speech_to_text()
#     recognizer.from_text_to_speech(text)






