#!/usr/bin/env python3

from gui.main_window import MainWindow
from PySide6.QtWidgets import QApplication


#    #    #    ###  #   #  
##  ##   # #    #   ##  #  
# ## #  #   #   #   # # #  
#    #  #####   #   # # #  
#    #  #   #   #   #  ##  
#    #  #   #  ###  #   # 

if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec()

