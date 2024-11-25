import sys
from modules.MainWindow import MainWindow

from PyQt6 import QtWidgets

def run():
    window()

def window():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
