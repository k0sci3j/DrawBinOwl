from PySide6.QtCore import Qt
from PySide6 import QtGui
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QDialogButtonBox,
                               QMessageBox, QFileDialog)
import struct
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # nie usuwać

class TableEditor(QDialog):
    def __init__(self, parent, arr, item_size, start_offset, datatype, x_name, y_name, mx, my, full_file_bytes):
        super().__init__(parent)
        self.setWindowTitle("Map editor")
        self.arr = arr
        self.item_size = item_size
        self.start_offset = start_offset
        self.datatype = datatype
        self.mx = mx
        self.my = my
        self.full_file_bytes = bytearray(full_file_bytes)  # mutable copy of whole file
        self.fmt = {
            "uint8": ("B", 1), "int8": ("b", 1),
            "uint16_le": ("<H", 2), "uint16_be": (">H", 2),
            "int16_le": ("<h", 2), "int16_be": (">h", 2),
            "uint32_le": ("<I", 4), "uint32_be": (">I", 4),
            "int32_le": ("<i", 4), "int32_be": (">i", 4),
            "float32_le": ("<f", 4), "float32_be": (">f", 4),
        }[datatype][0]

        layout = QVBoxLayout(self)

        self.table = QTableWidget(self.mx, self.my)
        layout.addWidget(self.table)

        col_labels = [(f"{y_name}{j}" if y_name else f"col{j}") for j in range(self.my)]
        row_labels = [(f"{x_name}{i}" if x_name else f"row{i}") for i in range(self.mx)]
        self.table.setHorizontalHeaderLabels(col_labels)
        self.table.setVerticalHeaderLabels(row_labels)

        Z = self.arr[: self.mx * self.my].reshape((self.mx, self.my))
        for i in range(self.mx):
            for j in range(self.my):
                val = Z[i, j]
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.table.setItem(i, j, item)

        self.colorize_table(Z)

        buttons_layout = QHBoxLayout()
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        buttons.accepted.connect(self.save_modified_bin)  # Save
        buttons.rejected.connect(self.reject)  # Close
        buttons_layout.addWidget(buttons)

        legend = QLabel("HOWTO:\n+ : +1, - : -1\n> : +5%, < : -5%")
        legend.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        buttons_layout.addWidget(legend)
        layout.addLayout(buttons_layout)

    def colorize_table(self, Z):
        import matplotlib.cm as cm
        import matplotlib.colors as colors

        try:
            vmin = float(np.min(Z))
            vmax = float(np.max(Z))
        except Exception:
            vmin, vmax = 0.0, 1.0

        if vmin == vmax:
            vmax = vmin + 1.0

        norm = colors.Normalize(vmin=vmin, vmax=vmax)
        cmap = cm.get_cmap("viridis")

        for i in range(self.mx):
            for j in range(self.my):
                val = float(Z[i, j])
                rgba = cmap(norm(val))
                r = int(rgba[0] * 255)
                g = int(rgba[1] * 255)
                b = int(rgba[2] * 255)

                luminance = 0.299 * r + 0.587 * g + 0.114 * b
                text_color = QtGui.QColor(0, 0, 0) if luminance > 150 else QtGui.QColor(255, 255, 255)

                item = self.table.item(i, j)
                if item:
                    item.setBackground(QtGui.QColor(r, g, b))
                    item.setForeground(text_color)

    def keyPressEvent(self, event):
        key = event.key()
        selected_items = self.table.selectedItems()
        if not selected_items:
            return super().keyPressEvent(event)

        for item in selected_items:
            try:
                val = float(item.text())
            except ValueError:
                continue

            if key == Qt.Key_Plus or key == Qt.Key_Equal:
                val += 1
            elif key == Qt.Key_Minus:
                val -= 1
            elif key == Qt.Key_Greater:
                val *= 1.05
            elif key == Qt.Key_Less:
                val *= 0.95
            else:
                continue

            if self.fmt.lower().find("f") == -1:
                val = int(round(val))

            item.setText(str(val))

        Z = np.zeros((self.mx, self.my))
        for i in range(self.mx):
            for j in range(self.my):
                try:
                    Z[i, j] = float(self.table.item(i, j).text())
                except:
                    Z[i, j] = 0
        self.colorize_table(Z)

    def save_modified_bin(self):
        values = []
        for i in range(self.mx):
            for j in range(self.my):
                item = self.table.item(i, j)
                if item is None:
                    values.append(self.arr[i * self.my + j])
                    continue
                txt = item.text().strip()
                if txt == "":
                    values.append(self.arr[i * self.my + j])
                    continue
                if self.fmt.lower().find("f") != -1:
                    try:
                        v = float(txt)
                    except Exception:
                        QMessageBox.critical(self, "Error", f"Wrong value in ({i},{j}): {txt}")
                        return
                else:
                    try:
                        if txt.startswith("0x") or txt.startswith("-0x"):
                            v = int(txt, 16)
                        else:
                            v = int(txt, 10)
                    except Exception:
                        QMessageBox.critical(self, "Error", f"Wrong value in ({i},{j}): {txt}")
                        return
                values.append(v)

        packed = bytearray()
        try:
            for v in values:
                packed += struct.pack(self.fmt, v)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot pack: {e}")
            return

        end = self.start_offset + len(packed)
        if end > len(self.full_file_bytes):
            QMessageBox.critical(self, "Error", "Data is bigger than file")
            return
        self.full_file_bytes[self.start_offset:end] = packed

        out_path, _ = QFileDialog.getSaveFileName(self, "Save modified .bin file as...", "", "BIN (*.bin);;All files (*)")
        if not out_path:
            return

        try:
            with open(out_path, "wb") as f:
                f.write(self.full_file_bytes)
            QMessageBox.information(self, "Saved", f"Modified .bin file saved as:\n{out_path}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot write file:\n{e}")
