from PyQt6 import uic
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
import numpy as np

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
max_T_default = 25

def main():
    Form, Window = uic.loadUiType("main_window.ui")
    app = QApplication([])
    window = Window()
    form = Form()
    form.setupUi(window)
    
    from tableHandlers import TableHandler

    cTable = TableHandler(form.cMatrix, cMatrixDefault)
    tTable = TableHandler(form.tMatrix, tMatrixDefault)
    cTable.table.itemChanged.connect(TableHandler.floatValidateAndMessage)
    tTable.table.itemChanged.connect(TableHandler.floatValidateAndMessage)

    from optimizer import MatrixOptimizer

    matrixOptimizer = MatrixOptimizer(cTable, tTable, max_T_default)

    form.matrixInput.clicked.connect(lambda: (
        cTable.toNumpy(),
        tTable.toNumpy()
    ))
    form.optimize1.clicked.connect(lambda: (
        matrixOptimizer.optimization1(),
        print(matrixOptimizer.eliminated)
    ))
    #form.optimize2.clicked.connect(matrixOptimizer.optimization2)
    form.optimize2.clicked.connect(lambda: (
        matrixOptimizer.optimization2(),
        print(matrixOptimizer.eliminated)
    ))

    validator = QRegularExpressionValidator(QRegularExpression(r'[0-9]+\.[0-9]*'))
    form.T_max_lEdit.setValidator(validator)


    window.show()
    app.exec()

if __name__ == '__main__':
    main()