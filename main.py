from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel, QScrollArea
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QRegularExpressionValidator, QPainter
from userInfo import DataGetter
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

def InputBtnClick(dataGetter: DataGetter, matrixOptimizer, inputBtn: QPushButton, instructionLabel: QLabel, actionBtns: list):
    modes = {
        'input': 'Ввод данных',
        'reset': 'Ввести новые данные'
    }
    instructionTexts = {
        'input': 'Введите данные',
        'reset': 'Выберите действие'
    }

    if dataGetter.inputBtnMode == 'input':
        gotError: bool = dataGetter.catch_input_errors()
        if not gotError:
            [ tableHandler.table.setEnabled(False) for tableHandler in dataGetter.tables.values()]
            [ lineEdit.setEnabled(False) for lineEdit in dataGetter.lineEdits.values()]
            [ btn.setEnabled(True) for btn in actionBtns]
            inputBtn.setText(modes['reset'])
            dataGetter.inputBtnMode = 'reset'
            instructionLabel.setText(instructionTexts['reset'])
            matrixOptimizer.max_T = float(dataGetter.lineEditsTexts['Значение Тз'])

        return
    
    if dataGetter.inputBtnMode == 'reset':
        [ tableHandler.table.setEnabled(True) for tableHandler in dataGetter.tables.values()]
        [ tableHandler.decolorize_cells() for tableHandler in dataGetter.tables.values()]
        [ lineEdit.setEnabled(True) for lineEdit in dataGetter.lineEdits.values()]
        [ btn.setEnabled(False) for btn in actionBtns]
        inputBtn.setText(modes['input'])
        dataGetter.inputBtnMode = 'input'
        instructionLabel.setText(instructionTexts['input'])
        return        


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
    dataGetter = DataGetter(tables={"Матрица C": cTable, "Матрица T": tTable}, lineEdits={"Значение Тз": form.T_max_lEdit}, 
                            lineEditsLinkedTables={"Значение Тз": 'Матрица T'})

    form.dataInput.clicked.connect(lambda: (
        InputBtnClick(dataGetter, matrixOptimizer, form.dataInput, form.instructionLabel, [form.optimize1, form.optimize2, form.decisionTreeBtn]),
        matrixOptimizer.refreshValues()
    ))
    form.optimize1.clicked.connect(lambda: (
        matrixOptimizer.optimization1(),
        matrixOptimizer.cTable.colorize_cells(matrixOptimizer.eliminated),
        matrixOptimizer.tTable.colorize_cells(matrixOptimizer.eliminated)
    ))
    form.optimize2.clicked.connect(lambda: (
        matrixOptimizer.optimization2(),
        matrixOptimizer.cTable.colorize_cells(matrixOptimizer.eliminated),
        matrixOptimizer.tTable.colorize_cells(matrixOptimizer.eliminated)
    ))
    form.decisionTreeBtn.clicked.connect(lambda: (
        matrixOptimizer.tree_optimization(),
        form.svgView.update()
    ))

    validator = QRegularExpressionValidator(QRegularExpression(r'[0-9]+\.[0-9]*'))
    form.T_max_lEdit.setValidator(validator)
    form.T_max_lEdit.setText(str(max_T_default))
    
    def showSVG(event):
        if matrixOptimizer.treeDone:
            svgRenderer = QSvgRenderer('out.svg')
            painter = QPainter(form.svgView)
            svgRenderer.render(painter)
    form.svgView.paintEvent = showSVG
    window.show()
    app.exec()

if __name__ == '__main__':
    main()