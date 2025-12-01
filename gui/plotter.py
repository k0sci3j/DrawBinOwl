import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

class BinPlotter:
    def __init__(self):
        self.mw = None

    def plotter_2d(self, arr, x_addr):
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(x_addr, arr, marker='.', markersize=3, linewidth=1)
        ax.set_title(f"{self.mw.file_path}\nName: {self.mw.map_name.text()}, Datatype: {self.mw.combo_format.currentText()}, Addr range: {self.mw.edit_min.text()} - {self.mw.edit_max.text()}")
        ax.set_xlabel("ADDR")
        ax.set_ylabel("VALUE")
        ax.grid(True)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: hex(int(x))))
        plt.show()

    def plotter_3d(self, arr):
        data_len = len(arr)
        try:
            mx = int(self.mw.map_x.text())
            my = int(self.mw.map_y.text())
        except ValueError:
            side = int(np.sqrt(data_len))
            mx = my = side
    
        if mx * my > data_len:
            QMessageBox.critical(self, "Error", "X * Y > data length")
            return
    
        Z = arr[:mx * my].reshape((mx, my))
        X = np.arange(mx)
        Y = np.arange(my)
        X, Y = np.meshgrid(X, Y)
    
        xlabel = self.mw.name_x.text() or "X"
        ylabel = self.mw.name_y.text() or "Y"
    
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection="3d")
        ax.plot_surface(X, Y, Z.T, cmap="viridis")
        ax.set_title(f"{self.mw.file_path}\nName: {self.mw.map_name.text()}, Datatype: {self.mw.combo_format.currentText()}, Addr range: {self.mw.edit_min.text()} - {self.mw.edit_max.text()}")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel("Value")
        plt.show()

