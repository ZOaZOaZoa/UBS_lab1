from PyQt6.QtWidgets import QTableWidget
from tableHandlers import TableHandler
import numpy as np

class MatrixOptimizer:
    def __init__(self, cTable: TableHandler, tTable: TableHandler, max_T: float):
        self.max_T = max_T
        self.cTable: TableHandler = cTable
        self.tTable: TableHandler = tTable
        self.cMatrix: np.array = cTable.matrix
        self.tMatrix: np.array = tTable.matrix
        self.rows, self.columns = self.cMatrix.shape
        self.eliminated = np.zeros((self.rows, self.columns), dtype=bool)

    def refreshValues(self):
        self.cMatrix = self.cTable.matrix
        self.tMatrix = self.tTable.matrix
        self.rows, self.columns = self.cMatrix.shape
        self.eliminated = np.zeros((self.rows, self.columns), dtype=bool)   

    def optimization1(self):
        c_argmin = self.cMatrix.argmin(1)
        eliminated = []
        for i in range(self.rows):
            t_min = self.tMatrix[i,c_argmin[i]]
            c_min = self.cMatrix[i,c_argmin[i]]
            eliminated.append([ self.tMatrix[i,j] > t_min or (self.tMatrix[i,j] == t_min and self.cMatrix[i,j] > c_min) for j in range(self.columns) ])

        self.eliminated = np.logical_or(self.eliminated, np.array(eliminated, dtype=bool))
        return self.eliminated
    
    def optimization2(self):
        t_min = self.tMatrix.min(1)
        t_min_sum = sum(t_min)
        eliminated = []
        for i in range(self.rows):
            eliminated.append([ t_min_sum - t_min[i] + self.tMatrix[i,j] > self.max_T for j in range(self.columns) ])

        self.eliminated = np.logical_or(self.eliminated, np.array(eliminated, dtype=bool))
        return self.eliminated

    