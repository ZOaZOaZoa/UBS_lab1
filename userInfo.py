from PyQt6.QtWidgets import QMessageBox

def showMessageBox(title: str, description: str, icon: QMessageBox.Icon):
    msgBox = QMessageBox()
    msgBox.setText(title)
    msgBox.setInformativeText(description)
    msgBox.setIcon(icon)
    msgBox.exec()

class TemplateMessageBox(QMessageBox):
    def __init__(self, title: str, description: str, icon: QMessageBox.Icon):
        super().__init__()
        self.setText(title)
        self.setInformativeText(description)
        self.setIcon(icon)

class DataGetter:
    def __init__(self, tables: dict, lineEdits: dict, lineEditsLinkedTables: dict = {}):
        '''
        tables -> dict(str: TableHandler)
        lineEdits -> dict(str: QLineEdit)
        '''
        self.tables = tables
        self.lineEdits = lineEdits
        self.data_good = False
        self.lineEditsTexts = dict()
        self.lineEditsLinkedTables = lineEditsLinkedTables
        self.inputBtnMode = 'input'

    def _get_and_check(self):
        '''
        Считывает данные из полей для ввода и выполняет проверки на корректность введённых данных
        '''
        for name, table in self.tables.items():
            table.toNumpy()
            if not table.data_good:
                raise ValueError(f"{name}. Неверно введённые данные")
            
        for name, lineEdit in self.lineEdits.items():
            text = lineEdit.text()
            if len(text) == 0:
                raise ValueError(f"{name}. Должно быть введено значение")
            self.lineEditsTexts[name] = text
            
            
            if name not in self.lineEditsLinkedTables:
                return
            
            table_name = self.lineEditsLinkedTables[name]
            theorMin = self.tables[table_name].theorMin
            if float(text) < theorMin:
                raise ValueError(f"{name}. Значение не может быть меньше теоретического минимума равного {theorMin}")
            
    def catch_input_errors(self) -> bool:
        try:
            self._get_and_check()
            msg = TemplateMessageBox("Данные успешно введены", "", QMessageBox.Icon.Information)
            msg.exec()
            return False
        except ValueError as e:
            msg = TemplateMessageBox("Неверно введённые данные", str(e), QMessageBox.Icon.Warning)
            msg.exec()
            return True