from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from userInfo import TemplateMessageBox
import numpy as np

class TableHandler:
    valueErrorTitle: str = 'Введены неверные данные!'
    valueErrorMessages: dict = {
        'empty_cell': TemplateMessageBox(valueErrorTitle, 'Заполните все ячейки матрицы.', QMessageBox.Icon.Warning),
        'non_float': TemplateMessageBox(valueErrorTitle, 'Все значения должны быть числовыми.', QMessageBox.Icon.Warning),
        'negative_value': TemplateMessageBox(valueErrorTitle, 'Значение не может быть отрицательным.', QMessageBox.Icon.Warning)
    }

    def __init__(self, table: QTableWidget, defaultValues: np.array = None):
        self.table: QTableWidget = table
        self.rows = self.table.rowCount()
        self.columns = self.table.columnCount()
        self.matrix: np.ndarray = defaultValues
        self.data_good = True
        self.theorMin = None

        if self.matrix is None:
            self.data_good = False
            return

        if (self.rows, self.columns) != self.matrix.shape:
            raise ValueError("Table shape does not match passed defaultValues: np.array shape")
        
        self.toTable(self.matrix)

    @staticmethod
    def floatValidate(item: QTableWidgetItem):
        '''
        Валидирует значение в соответствии со следующими критериями: значение непустое, вещественное типа float, неотрицательное. Возвращает код результата проверки и само проверенное значение, если оно прошло валидацию.
        '''
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
        '''
        Валидирует введённое значение и выводит сообщение, если значение не прошло валидацию. Проверяемые критерии определяются floatValidate()
        '''
        status, value = TableHandler.floatValidate(item)
        if status != 'good':
            TableHandler.valueErrorMessages[status].exec()
            return ('err', None)
        
        return ('good', value)

    def _calcTheorMin(self):
        '''
        Расчёт теоретического суммарного минимума для набора из единичных значений из каждой строки 
        '''
        self.theorMin = sum(self.matrix.min(1))

    def toNumpy(self):
        '''
        Запись значений из таблицы QTableWidget в матрицу np.array
        '''
        matrix = []
        for i in range(self.table.rowCount()):
            row = []
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                
                status, value = TableHandler.floatValidateAndMessage(item)
                if status == 'err':
                    self.table.setCurrentCell(i, j)
                    self.data_good = False
                    return None
                    
                row += [value,]
            matrix += [row,]
        
        np_matrix = np.array(matrix, dtype=np.float16)
        self.matrix = np_matrix
        self.data_good = True
        self._calcTheorMin()
        return np_matrix

    def toTable(self, matrix: np.array):
        '''
        Запись значений из матрицы np.array в таблицу QTableWidget
        '''
        if (self.rows, self.columns) != matrix.shape:
            raise ValueError("Table shape does not match passed np.array shape")

        for i in range(self.rows):
            for j in range(self.columns):
                value = QTableWidgetItem(str(matrix[i,j]))
                self.table.setItem(i, j, value)