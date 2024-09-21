from PyQt6 import uic
from PyQt6.QtWidgets import QApplication
import numpy as np

def main():
    Form, Window = uic.loadUiType("main_window.ui")
    app = QApplication([])
    window = Window()
    form = Form()
    form.setupUi(window)
    
    from tableHandlers import TableHandler

    cMatrixDefault = np.array([
        [4.5, 7, 2, 2],
        [5, 8, 1, 3],
        [5.5, 9, 6, 2],
        [6, 10, 7, 1],
        [6.5, 7, 3, 1]
    ], dtype=np.float16)

    tMatrixDefault = np.array([
        [4.5, 3, 2, 9],
        [5, 6, 5, 10],
        [5.5, 7, 6, 11],
        [6, 8, 7, 12],
        [6.5, 9, 8, 5]
    ], dtype=np.float16)

    cTable = TableHandler(form.cMatrix, cMatrixDefault)
    tTable = TableHandler(form.tMatrix, tMatrixDefault)

    form.cInput.clicked.connect(cTable.toNumpy)
    form.tInput.clicked.connect(tTable.toNumpy)
    form.test.clicked.connect(lambda: print(cTable.matrix, tTable.matrix, sep='\n\n'))

    cTable.table.itemChanged.connect(TableHandler.floatValidateAndMessage)
    tTable.table.itemChanged.connect(TableHandler.floatValidateAndMessage)

    window.show()
    app.exec()
    
def test(*args):
    print(args)

if __name__ == '__main__':
    main()