import sys

import pandas as pd
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import *
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, QObject, Signal, Slot, QModelIndex

import Cleaning

current_dataset = "Current Dataset:\n"
mode_day = True


class SideWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.MinimumExpanding)

        QtWidgets.QSizePolicy.setHorizontalStretch(self.sizePolicy(), 1)

    def sizeHint(self):
        return QtCore.QSize(40, 120)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('black'))
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Pipeline 37 App")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        self.info_box = StatusWindow('orange')

        layout1 = QHBoxLayout()
        status_panel = QVBoxLayout()
        main_panel = QTabWidget()

        info_box = StatusWindow('orange')
        info_box.setMinimumSize(100, 200)
        status_panel.addWidget(info_box)

        self.status_button = QPushButton("Status window button 2")
        self.status_button.setCheckable(True)
        status_panel.addWidget(self.status_button)
        # Connect button click to fetch_text method in backend
        self.status_button.clicked.connect(info_box.fetch_text_from_backend)

        status_area = AreaWidget('purple')
        status_panel.addWidget(status_area)
        layout1.addLayout(status_panel)
        # Add side window here then reposition when it works

        # Window with data sample
        data_display = DataDisplayWindow('green')
        layout1.addWidget(data_display)

        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)


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

        self.table = QtWidgets.QTableView()
        d = {'col1': [1, 2, 3], 'col2': [4, None, 6], 'col3': [8.19
            , None, 8.5], 'col4': [1.2, None, None]}
        df = pd.DataFrame(data=d)

        self.model = TableModel(df)
        self.table.setModel(self.model)
        layout.addWidget(self.table)
        add_df_button = QPushButton("Add data")
        add_df_button.clicked.connect(self.fetch_data_from_backend)
        layout.addWidget(add_df_button)
        self.setLayout(layout)

    def fetch_data_from_backend(self):
        backend = Cleaning.StatusEmitter()
        backend.send_df.connect(self.update_data)
        backend.dataframe_sender()

    def update_data(self, nu_data):
        print(nu_data)
        pd.options.future.infer_string = True
        # Update data in the model
        self.model.set_dataframe(nu_data)



class StatusWindow(QWidget):
    past_status_text = 'past'

    def __init__(self, color: str):
        super(StatusWindow, self).__init__()
        self.active_status = QLabel('active')
        self.past_status = QLabel(self.past_status_text)

        self.setAutoFillBackground(True)
        layout = QtWidgets.QVBoxLayout()

        self.status_button = QPushButton("Generate test series")
        self.status_button.setCheckable(True)
        layout.addWidget(self.status_button)
        # Connect button click to fetch_text method in backend
        self.status_button.clicked.connect(self.fetch_text_from_backend)

        self.status_button = QPushButton("Generate test dataframe")
        self.status_button.setCheckable(True)
        layout.addWidget(self.status_button)
        # Connect button click to fetch_text method in backend
        self.status_button.clicked.connect(self.fetch_text_from_backend)

        layout.addWidget(QLabel("TestTestTest"))
        layout.addWidget(self.past_status)
        layout.addWidget(self.active_status)
        self.setLayout(layout)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

    def fetch_text_from_backend(self):
        backend = Cleaning.StatusEmitter()
        backend.send_string.connect(self.update_text_label)
        backend.run_test_function('Chaotic fish')

    def update_text_label(self, text):
        self.active_status.setText(text)


class AreaWidget(QWidget):

    def __init__(self, color):
        super(AreaWidget, self).__init__()
        self.setAutoFillBackground(True)

        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.MinimumExpanding)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

