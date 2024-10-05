from PyQt6.QtWidgets import QTableWidget
from tableHandlers import TableHandler
import numpy as np

class Tree:
    def __init__(self, parent: 'Tree' = None, fixed_nodes: list = []):
        self.parent: Tree = parent
        self.children = dict()
        self.fixed_nodes = fixed_nodes
        self.status_good = True

    def add_child(self, fixed_nodes, c_sum, t_sum) -> 'Tree':
        parent_node = self.find_child(fixed_nodes[:-1])
        child_node = Tree(parent_node, fixed_nodes.copy())
        child_node.set_metrics(c_sum, t_sum)
        last_node = fixed_nodes[-1]
        parent_node.children[last_node] = child_node

        return child_node
    
    def find_child(self, fixed_nodes) -> 'Tree':
        if self.fixed_nodes == fixed_nodes:
            return self
        
        next_node = fixed_nodes[len(self.fixed_nodes)]
        res = self.children[next_node].find_child(fixed_nodes)
        return res

    def set_metrics(self, c_sum, t_sum):
        self.c_sum = c_sum
        self.t_sum = t_sum

    def set_status(self, status_good: bool):
        self.status_good = status_good

    def print_node(self):
        print(f'{self.c_sum:5>}|{self.t_sum:5>} good:{repr(self.status_good)}')

    def print_tree(self, level = 1):
        if level == 1:
            self.print_node()
        for node, child in self.children.items():
            print('| '*level + f'{node}'+ '-->', end='')
            child.print_node()
            child.print_tree(level+1)

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
    
    def tree_add_current_row_nodes(self, fixed_nodes, row, c_argmin, t_argmin):
        current_row_good_nodes = []
        for j in range(self.columns):
            if self.eliminated[row,j]:
                continue
            
            fixed_nodes[row] = j
            c_sum = sum(self.cMatrix[range(row+1),fixed_nodes])
            c_sum += sum(self.cMatrix[range(row+1, self.rows),c_argmin[row+1:]])
            t_sum = sum(self.tMatrix[range(row+1),fixed_nodes])
            t_sum += sum(self.tMatrix[range(row+1, self.rows),t_argmin[row+1:]])
            node = self.root.add_child(fixed_nodes, c_sum, t_sum)
            if t_sum > self.max_T:
                node.status_good = False
            else:
                current_row_good_nodes.append(node)
        return current_row_good_nodes


    def tree_optimization(self):
        c_argmin = self.cMatrix.argmin(1)
        t_argmin = self.tMatrix.argmin(1)

        fixed_nodes = []
        c_sum = sum(self.cMatrix[range(self.rows),c_argmin])
        t_sum = sum(self.tMatrix[range(self.rows),t_argmin])
        self.root = Tree()
        self.root.set_metrics(c_sum, t_sum)
        self.root.set_status(status_good=True)

        for i in range(self.rows):
            fixed_nodes.append(0)
            current_row_good_nodes = self.tree_add_current_row_nodes(fixed_nodes, i, c_argmin, t_argmin)
            
            min_c = current_row_good_nodes[0].c_sum
            ind = current_row_good_nodes[0].fixed_nodes[-1]
            for i, node in enumerate(current_row_good_nodes):
                if i == 0:
                    continue

                if node.c_sum < min_c:
                    min_c = node.c_sum
                    ind = node.fixed_nodes[-1]
            
            fixed_nodes[-1] = ind
            for node in current_row_good_nodes:
                if node.fixed_nodes[-1] != ind:
                    node.set_status(False)

        print('Дерево рассчитано')
        self.root.print_tree()
