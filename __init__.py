import sys
import FrontEnd as Front
from Cleaning import *
from FileProcessor import *


if __name__ == "__main__":
    app = Front.QApplication([])
    main_window = Front.MainWindow()
    main_window.show()
    app.exec()


