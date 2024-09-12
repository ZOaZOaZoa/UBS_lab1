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
