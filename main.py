import ui
from PyQt5.QtWidgets import QApplication
import sys
from intent_classifier.train import IntentClassifier


if __name__ == "__main__":

    # If model doesn't exist use this commands. After saving revert changes
    # ic = IntentClassifier()
    # ic.train()
    # ic.save("train_Data")

    App = QApplication([])
    window = ui.Window()

    sys.exit(App.exec())
