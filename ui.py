import sys
from PyQt5.QtWidgets import *

if __name__ == "__main__":
    app = QApplication([])

    w = QWidget()

    grid = QGridLayout(w)

    for i in range(3):
        for j in range(3):
            grid.addWidget(QPushButton("Button"),i,j)


    w.show()
    sys.exit(app.exec_())