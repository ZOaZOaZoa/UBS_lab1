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

class dataGetter:
    def __init__(self, tables: dict, lineEdits: dict):
        '''
        tables -> dict(str: TableHandler)
        lineEdits -> dict(str: QLineEdit)
        '''
        self.tables = tables
        self.lineEdits = lineEdits
        self.data_good = False
        self.lineEditsTexts = dict()

    def _get_and_check(self):
        for name, table in self.tables.items():
            table.toNumpy()
            if not table.data_good:
                raise ValueError(f"{name}. Неверно введённые данные")
            
        for name, lineEdit in self.lineEdits.items():
            text = lineEdit.text()
            if len(text) == 0:
                raise ValueError(f"{name}. Должно быть введено значение")
            self.lineEditsTexts[name] = text
            
    def catched_input_errors(self):
        try:
            self._get_and_check()
            return False
        except ValueError as e:
            msg = TemplateMessageBox("Неверно введённые данные", str(e), QMessageBox.Icon.Warning)
            msg.exec()
            return True