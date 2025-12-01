import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # nie usuwać
import json
from gui.table_editor import TableEditor
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QComboBox, QMessageBox, QLineEdit, QHBoxLayout
)
from PySide6.QtCore import Qt

from data.data_loader import load_bin_file
from gui.plotter import BinPlotter

 ###   #   #  ###  
#   #  #   #   #   
#      #   #   #   
#  ##  #   #   #   
#   #  #   #   #   
 ####   ###   ###

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DrawBinOwl")
        self.setFixedSize(self.size())

        self.file_path = None
        self.file_size = 0

        layout = QVBoxLayout()

        hbox = QHBoxLayout()
        self.label_path = QLabel("File: (Not available)")
        self.btn_open = QPushButton("Choose .bin file...")
        self.btn_open.clicked.connect(self.pick_file)
        hbox.addWidget(self.label_path)
        hbox.addWidget(self.btn_open)
        layout.addLayout(hbox)

        hbox = QHBoxLayout()
        self.map_name = QLineEdit("")
        hbox.addWidget(QLabel("Map name:"))
        hbox.addWidget(self.map_name)
        layout.addLayout(hbox)

        hbox = QHBoxLayout()
        self.combo_format = QComboBox()
        self.combo_format.addItems([
            "uint8", "int8",
            "uint16_le", "uint16_be",
            "int16_le", "int16_be",
            "uint32_le", "uint32_be",
            "int32_le", "int32_be",
            "float32_le", "float32_be",
        ])
        hbox.addWidget(QLabel("Datatype:"))
        hbox.addWidget(self.combo_format)
        layout.addLayout(hbox)

        # Offsets
        hbox = QHBoxLayout()
        self.edit_min = QLineEdit("0x0")
        self.edit_max = QLineEdit("0x0")
        hbox.addWidget(QLabel("Min offset (hex):"))
        hbox.addWidget(self.edit_min)
        hbox.addWidget(QLabel("Max offset (hex):"))
        hbox.addWidget(self.edit_max)
        layout.addLayout(hbox)

        # 3D plot XY size
        hbox2 = QHBoxLayout()
        self.map_x = QLineEdit("")
        self.map_y = QLineEdit("")
        hbox2.addWidget(QLabel("Map X size (option):"))
        hbox2.addWidget(self.map_x)
        hbox2.addWidget(QLabel("Map Y size (option):"))
        hbox2.addWidget(self.map_y)
        layout.addLayout(hbox2)

        # 3D axis names
        hbox3 = QHBoxLayout()
        self.name_x = QLineEdit("")
        self.name_y = QLineEdit("")
        hbox3.addWidget(QLabel("3D X name (option):"))
        hbox3.addWidget(self.name_x)
        hbox3.addWidget(QLabel("3D Y name (option):"))
        hbox3.addWidget(self.name_y)
        layout.addLayout(hbox3)

        self.btn_plot2d = QPushButton("Draw 2D")
        self.btn_plot3d = QPushButton("Draw 3D")
        self.btn_table = QPushButton("Open table to edit")
        self.btn_plot2d.clicked.connect(self.plot_2d)
        self.btn_plot3d.clicked.connect(self.plot_3d)
        self.btn_table.clicked.connect(self.open_table)
        layout.addWidget(self.btn_plot2d)
        layout.addWidget(self.btn_plot3d)
        layout.addWidget(self.btn_table)

        # Save/Load
        hbox = QHBoxLayout()
        self.btn_save_json = QPushButton("Save settings")
        self.btn_load_json = QPushButton("Load settings")
        self.btn_save_json.clicked.connect(self.save_settings)
        self.btn_load_json.clicked.connect(self.load_settings)
        hbox.addWidget(self.btn_save_json)
        hbox.addWidget(self.btn_load_json)
        layout.addLayout(hbox)

        self.setLayout(layout)
        self.resize(700, 400)
        self.plotter = BinPlotter()

    def pick_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Choose .bin file",
            filter=".bin (*.bin *.BIN);;All files (*)"
        )
        if file:
            self.load_file(file)

    def load_file(self, path):
        self.file_path = path
        self.label_path.setText(f"File: {path}")

        with open(path, "rb") as f:
            data = f.read()
        self.file_size = len(data)

        self.edit_min.setText("0x0")
        self.edit_max.setText(hex(self.file_size))

    def load_current_data(self):
        if not self.file_path:
            QMessageBox.critical(self, "Error", "Choose file!")
            return None, None

        datatype = self.combo_format.currentText()

        try:
            start_offset = int(self.edit_min.text(), 16)
            end_offset = int(self.edit_max.text(), 16)
        except ValueError:
            QMessageBox.critical(self, "Error", "Min/Max must be in hex")
            return None, None

        arr, item_size = load_bin_file(
            self.file_path, datatype,
            start_offset=start_offset,
            end_offset=end_offset
        )

        x_addr = np.arange(len(arr)) * item_size + start_offset
        return arr, x_addr

    def save_settings(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save settings", "", ".json (*.json)")
        if not path:
            return

        settings = {
            "file_path": self.file_path,
            "map_name": self.map_name.text(),
            "min_offset": self.edit_min.text(),
            "max_offset": self.edit_max.text(),
            "datatype": self.combo_format.currentText(),
            "map_x": self.map_x.text(),
            "map_y": self.map_y.text(),
            "x_axis_name": self.name_x.text(),
            "y_axis_name": self.name_y.text()
        }

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            QMessageBox.information(self, "Saved", f"Saved in: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot save:\n{str(e)}")

    def load_settings(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load settings", "", ".json (*.json)")
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                settings = json.load(f)

            file_path = settings.get("file_path")
            if file_path:
                self.load_file(file_path)  
            self.edit_min.setText(settings.get("min_offset", "0x0"))
            self.edit_max.setText(settings.get("max_offset", hex(self.file_size)))

            self.map_x.setText(settings.get("map_x", ""))
            self.map_y.setText(settings.get("map_y", ""))
            self.name_x.setText(settings.get("x_axis_name", ""))
            self.name_y.setText(settings.get("y_axis_name", ""))
            self.map_name.setText(settings.get("map_name", ""))

            datatype = settings.get("datatype", "uint8")
            if datatype in [self.combo_format.itemText(i) for i in range(self.combo_format.count())]:
                self.combo_format.setCurrentText(datatype)

            QMessageBox.information(self, "Loaded", f"Loaded: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot load:\n{str(e)}")

    def plot_2d(self):
        arr, x_addr = self.load_current_data()
        if arr is None:
            return
        self.plotter.mw = self
        self.plotter.plotter_2d(arr, x_addr)
        
    def plot_3d(self):
        arr, _ = self.load_current_data()
        if arr is None:
            return
        self.plotter.mw = self
        self.plotter.plotter_3d(arr)

    def open_table(self):
        arr_x = self.load_current_data()
        if arr_x is None:
            return
        arr, _ = arr_x

        data_len = len(arr)
        try:
            mx = int(self.map_x.text())
            my = int(self.map_y.text())
        except ValueError:
            side = int(np.sqrt(data_len))
            mx = my = side

        if mx * my > data_len:
            QMessageBox.critical(self, "Error", "Table too big")
            return

        try:
            with open(self.file_path, "rb") as f:
                full_bytes = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        xlabel = f"{self.name_x.text()} "
        ylabel = f"{self.name_y.text()} "

        datatype = self.combo_format.currentText()
        size_map = {
            "uint8": 1, "int8": 1,
            "uint16_le": 2, "uint16_be": 2,
            "int16_le": 2, "int16_be": 2,
            "uint32_le": 4, "uint32_be": 4,
            "int32_le": 4, "int32_be": 4,
            "float32_le": 4, "float32_be": 4,
        }
        item_size = size_map.get(datatype, 1)

        try:
            start_offset = int(self.edit_min.text(), 16)
        except:
            QMessageBox.critical(self, "Error", "Wrong start offset")
            return

        dlg = TableEditor(self, arr, item_size, start_offset, datatype, xlabel, ylabel, mx, my, full_bytes)
        dlg.exec()
