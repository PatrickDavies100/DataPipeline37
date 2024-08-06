import sys
import pyarrow
import AmazonUK.FrontEnd as Front
from AmazonUK.Cleaning import *
from AmazonUK.FileProcessor import *



if __name__ == "__main__":
    app = Front.QApplication([])
    main_window = Front.MainWindow()
    main_window.show()
    app.exec()


