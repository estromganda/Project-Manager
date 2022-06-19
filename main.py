import sys

from PyQt5.QtWidgets import QApplication

from MainWindow import MainWindow

app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.resize(900, 500)
mainWindow.showMaximized()
sys.exit(app.exec())
