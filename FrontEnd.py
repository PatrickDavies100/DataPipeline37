import sys

import pandas as pd
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import *
from PySide6.QtGui import QPalette, QColor, QAction
from PySide6.QtCore import Qt, QObject, Signal, Slot, QModelIndex

import Cleaning
import FileProcessor

current_dataset = "Current Dataset:\n"
mode_day = True
sample_n = 100  # Number of records displayed in sample dataframe


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

        # Tools area of screen
        tool_area = ToolWindow('purple')
        status_panel.addWidget(tool_area)
        layout1.addLayout(status_panel)

        # Context-sensitive window
        self.context_box = StatusWindow('orange')
        self.context_box.setMinimumSize(100, 200)
        status_panel.addWidget(self.context_box)
        self.rightSideLayout = QVBoxLayout()

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

        # Window with data sample
        self.stackLayout = QStackedLayout()
        self.rightSideLayout = QVBoxLayout()
        tabs_layout = QHBoxLayout()

        btn_data = QPushButton("Data")
        btn_data.pressed.connect(self.activate_tab_1)
        tabs_layout.addWidget(btn_data)
        data_display = DataDisplayWindow('green')
        self.stackLayout.addWidget(data_display)

        btn_process = QPushButton("Process")
        btn_process.pressed.connect(self.activate_tab_2)
        tabs_layout.addWidget(btn_process)
        process = AreaWidget('blue')
        self.stackLayout.addWidget(process)

        btn_active = QPushButton("Active")
        btn_active.pressed.connect(self.activate_tab_3)
        tabs_layout.addWidget(btn_active)
        active = AreaWidget('orange')

        self.stackLayout.addWidget(active)
        self.rightSideLayout.addLayout(tabs_layout)
        self.rightSideLayout.addLayout(self.stackLayout)
        layout1.addLayout(self.rightSideLayout)

        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)
        self.setStatusBar(QStatusBar(self))

    def activate_tab_1(self):
        self.stackLayout.setCurrentIndex(0)

    def activate_tab_2(self):
        self.stackLayout.setCurrentIndex(1)

    def activate_tab_3(self):
        self.stackLayout.setCurrentIndex(2)

    def signaller(self, context: int) -> None:
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
        add_df_button.clicked.connect(self.fetch_df_from_backend)
        layout.addWidget(add_df_button)
        self.setLayout(layout)

    def save_as_csv(self):
        print('save_as_csv activated in frontend')
        backend = FileProcessor.DataEmitter()
        backend.send_df.connect(self.update_df)
        backend.csv_reader()

    def fetch_df_from_backend(self):
        backend = FileProcessor.DataEmitter()
        backend.send_df.connect(self.update_df)
        backend.dataframe_sender()

    def update_df(self, new_data):
        """Changes the data being displayed"""
        pd.options.future.infer_string = True
        if sample_n <= len(new_data):
            self.model.set_dataframe(new_data.sample(sample_n).sort_index())
        else:
            self.model.set_dataframe(new_data.sort_index())


class StatusWindow(QWidget):
    # past_status_text = 'past'

    def __init__(self, color: str):
        super(StatusWindow, self).__init__()
        self.setAutoFillBackground(True)
        layout = QtWidgets.QVBoxLayout()

        self.setLayout(layout)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

    def reset(self, context: int) -> None:
        layout = QtWidgets.QVBoxLayout()
        if context == 1:
            layout.addWidget(QLabel("File to import:"))
            layout.addWidget(QLineEdit())
            layout.addWidget(QPushButton("Import"))
        self.setLayout(layout)



class ToolWindow(QWidget):
    """The window used for data processing tools"""
    def __init__(self, color: str):
        super(ToolWindow, self).__init__()
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.MinimumExpanding)

        main_layout = QtWidgets.QVBoxLayout()
        grid_layout = QtWidgets.QGridLayout()

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

        btn_test_function = QPushButton("Test function")
        btn_test_function.clicked.connect(self.test)
        grid_layout.addWidget(btn_test_function, 0, 0)

        btn_find_replace = QPushButton("Find and replace")
        grid_layout.addWidget(btn_find_replace, 0, 1)

        btn_confirm = QPushButton("Ok")
        btn_confirm.clicked.connect(self.confirm)
        grid_layout.addWidget(btn_confirm, 0, 1)


        main_layout.addLayout(grid_layout)

        self.setLayout(main_layout)

    def test(self):
        c = FileProcessor.CurrentDataFrame()
        print(c.get_dataframe())

    def confirm(self):
        # Run all temp_processes on CurrentDataFrame
        print ("Updating dataframe")
        FileProcessor.CurrentDataFrame.update_dataframe(FileProcessor.TempDataFrame.get_dataframe())

class AreaWidget(QWidget):

    def __init__(self, color):
        super(AreaWidget, self).__init__()
        self.setAutoFillBackground(True)

        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.MinimumExpanding)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


