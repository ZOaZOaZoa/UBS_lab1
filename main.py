def main():
    from PyQt6 import uic
    from PyQt6.QtWidgets import QApplication
    import numpy as np

    Form, Window = uic.loadUiType("main_window.ui")
    app = QApplication([])
    window = Window()
    form = Form()
    form.setupUi(window)
    
    from tableHandlers import TableReader

    cTable = TableReader(form.cMatrix)
    tTable = TableReader(form.tMatrix)

    form.cInput.clicked.connect(cTable.toNumpy)
    form.tInput.clicked.connect(tTable.toNumpy)

    form.test.clicked.connect(lambda: print(cTable.matrix, tTable.matrix, sep='\n\n'))

    window.show()
    app.exec()
    


if __name__ == '__main__':
    main()