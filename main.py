import ui
from PyQt5.QtWidgets import QApplication
import sys


if __name__ == "__main__":
    App = QApplication([])
    window = ui.Window()
    sys.exit(App.exec())
