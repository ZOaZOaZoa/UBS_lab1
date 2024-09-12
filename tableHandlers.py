from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from userInfo import TemplateMessageBox
import numpy as np

class TableReader:
    valueErrorTitle = 'Введены неверные данные!'
    valueErrorMessages = {
        'empty_cell': TemplateMessageBox(valueErrorTitle, 'Заполните все ячейки матрицы.', QMessageBox.Icon.Warning),
        'non_float': TemplateMessageBox(valueErrorTitle, 'Все значения должны быть числовыми.', QMessageBox.Icon.Warning),
        'negative_value': TemplateMessageBox(valueErrorTitle, 'Значение не может быть отрицательным.', QMessageBox.Icon.Warning)
    }

    def __init__(self, table: QTableWidget):
        self.table = table
        self.matrix = None

    @staticmethod
    def floatValidate(item: QTableWidgetItem):
        if not item:
            return ('empty_cell', None)
        
        try:
            item_f = float(item.text())
        except ValueError:
            return ('non_float', None)
        
        if item_f < 0:
            return ('negative_value', None)
        
        return ('good', item_f)
    
    @staticmethod
    def floatValidateAndMessage(item: QTableWidgetItem):
        status, value = TableReader.floatValidate(item)
        if status != 'good':
            TableReader.valueErrorMessages[status].exec()
            return ('err', None)
        
        return ('good', value)

    def toNumpy(self):
        matrix = []
        for i in range(self.table.rowCount()):
            row = []
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                
                status, value = TableReader.floatValidateAndMessage(item)
                if status == 'err':
                    self.table.setCurrentCell(i, j)
                    return None
                    
                row += [value,]
            matrix += [row,]
        
        np_matrix = np.array(matrix, dtype=np.float16)
        self.matrix = np_matrix
        return np_matrix
