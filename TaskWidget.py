import sys

from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QTextEdit, QApplication, QMenu, QInputDialog, QMessageBox

from Database import Database


class MySignals(QObject):
    stateChanged = pyqtSignal()


class TaskWidget(QTextEdit):
    stateChange = pyqtSignal()

    def __init__(self, text: str, database: Database, data={}):
        QTextEdit.__init__(self, text)
        self.database = database
        self.data = data
        self.signals = MySignals()
        self.setAlignment(Qt.AlignCenter)
        self.setMaximumHeight(70)
        self.setReadOnly(True)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu(self)
        actionEdith = menu.addAction("Edit")
        actionDelete = menu.addAction("Delete the task")

        actionCheckToDo = menu.addAction("To do")
        actionCheckToDo.setObjectName("1")
        actionCheckDoing = menu.addAction("Doing")
        actionCheckDoing.setObjectName("2")
        actionCheckDone = menu.addAction("Done")
        actionCheckDone.setObjectName("3")

        actionCheckToDo.setCheckable(True)
        actionCheckDoing.setCheckable(True)
        actionCheckDone.setCheckable(True)

        actionEdith.triggered.connect(self.editText)
        actionCheckToDo.triggered.connect(self.onStateChange)
        actionCheckDoing.triggered.connect(self.onStateChange)
        actionCheckDone.triggered.connect(self.onStateChange)
        actionDelete.triggered.connect(self.deleteTask)
        style = self.styleSheet()
        menu.setStyleSheet("")
        menu.exec(event.globalPos())

    def editText(self):
        styleSheet = self.styleSheet()
        if len(styleSheet) > 0:
            self.setStyleSheet("")
        newText = QInputDialog.getText(self, "", "Enter the new description")
        self.setStyleSheet(styleSheet)
        if newText[1] and len(newText[0]):
            self.setText(newText[0])
            self.setAlignment(Qt.AlignCenter)
            self.database.updateTask(idTask=self.data["id"], newDescription=newText[0], newState=self.data["state"])

    def onStateChange(self):
        oldState = self.data["state"]
        self.data["state"] = int(self.sender().objectName())
        print(type(oldState), type(self.data["state"]))
        self.database.updateTask(idTask=self.data["id"], newDescription=self.toPlainText(), newState=self.data["state"])
        if oldState != self.data["state"]:
            self.signals.stateChanged.emit()

    def deleteTask(self):
        style = self.styleSheet()
        self.setStyleSheet("")
        rep = QMessageBox.question(self, "", f"Do you want to delete the task: {self.toPlainText()}")
        if rep == QMessageBox.Yes:
            self.database.deleteTask(self.data["id"])
            self.deleteLater()
        self.setStyleSheet(style)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TaskWidget("WERTY", Database(), {"id": "4", "state": "TO DO"})
    w.show()
    sys.exit(app.exec())
