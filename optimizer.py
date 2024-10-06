from PyQt6.QtWidgets import QMessageBox
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
    
    def _calc_x_for_node(self, x_place):
        x_offset = (x_place - 1.5) * self.nodes_x_step
        x_offset + (self.image_width-self.node_width)/2
        x = x_offset + (self.image_width-self.node_width)/2
        return x
    
    def _calc_x_for_text(self, x_place):
        x_offset = (x_place - 1.5) * self.nodes_x_step
        x = x_offset + self.image_width/2
        return x

    def nodeSvg(self, node: 'Tree', x_place=1.5, level=0):
        if node.status_good:
            color = 'white'
        else:
            color = 'gray'
        y_baseline = level * self.level_step
        
        svg = f'''<rect x='{self._calc_x_for_node(x_place)}' y='{y_baseline}' width='{self.node_width}' height = '{self.node_height}' stroke='black' fill='{color}'/>
<text x='{self._calc_x_for_text(x_place)}' y='{y_baseline + self.node_height/2+3}' dominant-baseline='middle' text-anchor='middle' font-size='{self.f_size}'>{node.c_sum}|{node.t_sum}</text>\n'''
        return svg

    def nodesLevelSvg(self, children, level):
        y_baseline = level * self.level_step
        svg = f"<text x='0' y='{y_baseline + self.node_height/2}' font-size='{self.f_size}'>{level} уровень</text>\n"
        for j, node in children.items():
            svg += self.nodeSvg(node, j, level)
        return svg
        

    def toSvg(self, file_name: str ='out.svg'):
        self.image_width = 800*1.13
        self.image_height = 250*1.13
        self.node_width = 50
        self.node_height = 30
        self.f_size = '12px'
        self.level_step = 50
        self.nodes_x_step = self.node_width + 30

        svg = f'''<?xml version = '1.0' encoding='UTF-8'?>
<svg width='{self.image_width}' height='{self.image_height}' viewbox='0 0 {self.image_width} {self.image_height}' xmlns='http://www.w3.org/2000/svg'>
<text x='0' y='{self.node_height/2}' font-size='{self.f_size}'>0 уровень</text>
        '''
        svg += self.nodeSvg(self)
        valid_node = self
        level = 1
        while valid_node.children:
            svg += self.nodesLevelSvg(valid_node.children, level)
            level += 1
            y_baseline = (level-1) * self.level_step
            parent_y = y_baseline - self.level_step + self.node_height
            if valid_node.fixed_nodes:
                parent_x = self._calc_x_for_text(valid_node.fixed_nodes[-1])
            else:
                parent_x = self._calc_x_for_text(1.5)

            for node in valid_node.children.values():
                child_y = y_baseline
                child_x = self._calc_x_for_text(node.fixed_nodes[-1])
                svg += f"<line x1='{parent_x}' y1='{parent_y}' x2='{child_x}' y2='{child_y}' stroke='black'/>\n"
                if node.status_good:
                    valid_node = node
        
        
        svg += '</svg>'
        with open(file_name, 'w') as fp:
            fp.write(svg)

        

class MatrixOptimizer:
    def __init__(self, cTable: TableHandler, tTable: TableHandler, max_T: float):
        self.max_T = max_T
        self.cTable: TableHandler = cTable
        self.tTable: TableHandler = tTable
        self.cMatrix: np.array = cTable.matrix
        self.tMatrix: np.array = tTable.matrix
        self.rows, self.columns = self.cMatrix.shape
        self.eliminated = np.zeros((self.rows, self.columns), dtype=bool)
        self.treeDone = False

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

        
        self.root.print_tree()
        self.treeDone = True
        self.root.toSvg()
        msg = QMessageBox()
        msg.setText('Дерево успешно построено')
        msg.exec()