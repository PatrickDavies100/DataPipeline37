import sys

import pandas as pd
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import *
from PySide6.QtGui import QPalette, QColor, QAction
from PySide6.QtCore import Qt, QObject, Signal, Slot, QModelIndex

import FileProcessor

current_dataset = "Current Dataset:\n"
mode_day = True
sample_n = 5  # Number of records displayed in sample dataframe


class MainWindow(QMainWindow):
    button_clicked = Signal(int)
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Pipeline 37 App")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)

        toolbar = QToolBar("Main toolbar")
        self.addToolBar(toolbar)

        layout1 = QHBoxLayout()
        status_panel = QVBoxLayout()
        main_panel = QTabWidget()

        # Context-sensitive window
        self.context_box = StatusWindow('orange')
        self.context_box.setMinimumSize(100, 200)
        status_panel.addWidget(self.context_box)

        menu = self.menuBar()
        button_imp = QAction("Import dataset", self)
        button_imp.setStatusTip("Read a CSV or JSON file containing a dataset")
        button_imp.triggered.connect(self.signaller(1))
        button_imp.triggered.connect(self.context_box.reset(1))
        button_exp = QAction("Export dataset", self)
        button_exp.setStatusTip("Export the current dataset as a CSV or JSON file")
        button_save_pr = QAction("Save the current processes")
        button_load_pr = QAction("Load a set of data processes")
        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_imp)
        file_menu.addAction(button_exp)
        file_menu.addAction(button_save_pr)
        file_menu.addAction(button_load_pr)
        button_appearance = QAction("Data sample")
        options_menu = menu.addMenu("&Options")
        options_menu.addAction(button_appearance)

        # Purple area of screen
        status_area = AreaWidget('purple')
        status_panel.addWidget(status_area)
        layout1.addLayout(status_panel)

        # Window with data sample - working on 12/08/2024
        self.stacklayout = QStackedLayout()


        btn_data = QPushButton("Data display")
        btn_data.pressed.connect(self.activate_tab_1)
        layout1.addWidget(btn_data)
        data_display = DataDisplayWindow('green')


        btn_process = QPushButton("Process View")
        btn_process.pressed.connect(self.activate_tab_2)
        layout1.addWidget(btn_process)

        self.stacklayout.addWidget(data_display)
        self.stacklayout.addWidget(AreaWidget("green"))

        layout1.addLayout(self.stacklayout)

        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)
        self.setStatusBar(QStatusBar(self))

    def activate_tab_1(self):
        self.stacklayout.setCurrentIndex(0)

    def activate_tab_2(self):
        self.stacklayout.setCurrentIndex(1)

    def signaller(self, context: int) -> None:
        print('signaller function ' + str(context))
        self.button_clicked.emit(context)


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super().__init__(parent)
        self._dataframe = dataframe

    def rowCount(self, parent=QModelIndex()):
        return len(self._dataframe)

    def columnCount(self, parent=QModelIndex()):
        return len(self._dataframe.columns)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            value = self._dataframe.iloc[index.row(), index.column()]
            return str(value)
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._dataframe.columns[section]
            elif orientation == Qt.Vertical:
                return str(self._dataframe.index[section])
        return None

    def setData(self, index: QModelIndex, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self._dataframe.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole])
            return True
        return False

    def set_dataframe(self, new_dataframe: pd.DataFrame):
        self.beginResetModel()
        self._dataframe = new_dataframe
        self.endResetModel()

    def flags(self, index: QModelIndex):
        if index.isValid():
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.NoItemFlags


class DataDisplayWindow(QWidget):
    """The window with a sample of the current data displayed"""
    button_clicked = Signal(int)
    def __init__(self, color: str):
        super(DataDisplayWindow, self).__init__()

        self.setAutoFillBackground(True)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QLabel("Data Sample"))

        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.MinimumExpanding)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

        # Add data to initialise the table view
        self.table = QtWidgets.QTableView()
        d = {'col1': [0]}
        df = pd.DataFrame(data=d)

        self.model = TableModel(df)
        self.table.setModel(self.model)
        layout.addWidget(self.table)
        import_button = QPushButton("Save process")
        import_button.clicked.connect(self.save_as_csv)
        layout.addWidget(import_button)

        add_df_button = QPushButton("Add test data")
        add_df_button.clicked.connect(self.fetch_data_from_backend)
        layout.addWidget(add_df_button)
        self.setLayout(layout)

    def save_as_csv(self):
        print('save_as_csv activated in frontend')
        backend = FileProcessor.DataEmitter()
        backend.send_df.connect(self.update_data)
        backend.csv_reader()

    def fetch_data_from_backend(self):
        backend = FileProcessor.DataEmitter()
        backend.send_df.connect(self.update_data)
        backend.dataframe_sender()

    def update_data(self, new_data):
        """Changes the data being displayed"""
        pd.options.future.infer_string = True
        self.model.set_dataframe(new_data.sample(sample_n))


class StatusWindow(QWidget):
    # past_status_text = 'past'

    def __init__(self, color: str):
        super(StatusWindow, self).__init__()
        self.setAutoFillBackground(True)
        layout = QtWidgets.QVBoxLayout()

        self.status_button = QPushButton("Generate test dataframe")
        self.status_button.setCheckable(True)
        layout.addWidget(self.status_button)
        # Connect button click to fetch_text method in backend
        #self.status_button.clicked.connect(self.fetch_text_from_backend)

        self.setLayout(layout)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

    def reset(self, context: int) -> None:
        if context == 1:
            print('1')
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(QLabel("File to import:"))
            layout.addWidget(QLineEdit())
            layout.addWidget(QPushButton("Import"))
        self.setLayout(layout)

class AreaWidget(QWidget):

    def __init__(self, color):
        super(AreaWidget, self).__init__()
        self.setAutoFillBackground(True)

        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.MinimumExpanding)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


