import os
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QStandardItemModel, QKeySequence
from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog, QMenu, QTextEdit, QAction, QFontDialog, qApp, \
    QFileDialog
from PyQt5.QtWidgets import QWidget, QMainWindow, QDockWidget, QVBoxLayout, QLabel, QScrollArea, QSplitter, \
    QPushButton, QTableView, QGridLayout
from PyQt5.QtXml import QDomDocument

from Database import Database
from TaskWidget import TaskWidget

toDoBackground = "#B9F6CA"
doingBackground = "#8BC34A"
doneBackground = "#2E7D32"
pojectName = "Project Manager"


def customLabel(txt: str, font=None):
    label = QLabel(txt)
    label.setAlignment(Qt.AlignCenter)
    if font:
        label.setFont(font)
    return label


class MainWindow(QMainWindow):
    readProject = pyqtSignal(int)
    readTask = pyqtSignal(int)

    def __init__(self):
        QMainWindow.__init__(self)
        self.toolBarFile = self.addToolBar("File")
        qApp.setApplicationName(pojectName)
        self.currentProject = None
        self.actionNewProject = QAction("New Project")
        self.actionImportProject = QAction("Import a project")
        self.menuRescent = QMenu("Ressents projects")
        self.menuExport = QMenu("Export project as", self)
        self.actionDeleteProject = QAction("Delete current project")
        self.actionRenameProject = QAction("Rename current project")
        self.actionCloseProject = QAction("Close current project")
        self.actionNewTask = QAction("New Task")
        self.btnAllProject = QPushButton("All projects")

        self.database = Database()
        self.tableProject = QTableView()
        self.projectModel = QStandardItemModel()
        self.leftDockWidget = QDockWidget()
        self.centralWidget = QWidget()
        self.lefDockWidgetLayout = QVBoxLayout()

        self.projectName = QTextEdit("None Project")
        self.projectName.setAlignment(Qt.AlignCenter)
        self.projectName.setReadOnly(True)
        self.projectName.setFont(QFont("", 16))
        self.projectName.setMaximumHeight(60)
        self.projectName.setStyleSheet("background-color: #1976D2; border: 1px solid #009688; text-align: center;")

        # Central widget
        self.toDoWidget = QScrollArea()
        self.toDoWidget.setStyleSheet("QScrollArea{background-color: toDoBg}".replace("toDoBg", toDoBackground))
        self.doingWidget = QScrollArea()
        self.doingWidget.setStyleSheet("QScrollArea{background-color: doingBg}".replace("doingBg", doingBackground))
        self.doneWidget = QScrollArea()
        self.doneWidget.setStyleSheet("QScrollArea{background-color: doneBg}".replace("doneBg", doneBackground))

        self.createMenu()
        self.createToolBar()
        self.createCentralWidget()
        # self.createLeftDockWidget()

        self.labelStatistic = customLabel("Statistic")
        self.statusBar().setStyleSheet("font-size: 18px; background-color: #009688")
        self.statusBar().layout().setAlignment(Qt.AlignHCenter)
        self.statusBar().addWidget(self.labelStatistic)
        self.loadProjects()
        try:
            qApp.setFont(self.database.getPreferences()["font"])
        except Exception as e:
            print(e)

    def createCentralWidget(self):
        splitter = QSplitter()
        toDoContainer, doingContainer, doneContainer = QWidget(), QWidget(), QWidget()

        toDoContainer.setLayout(QVBoxLayout())
        toDoContainer.layout().addWidget(customLabel("<h1>To Do</h1>"))
        toDoContainer.layout().addWidget(self.toDoWidget)
        self.toDoWidget.setWidget(QWidget())
        self.toDoWidget.widget().setLayout(QGridLayout())
        self.toDoWidget.setAlignment(Qt.AlignHCenter)
        splitter.addWidget(toDoContainer)

        doingContainer.setLayout(QVBoxLayout())
        doingContainer.layout().addWidget(customLabel("<h1>Doing</h1>"))
        doingContainer.layout().addWidget(self.doingWidget)
        self.doingWidget.setWidget(QWidget())
        self.doingWidget.widget().setLayout(QGridLayout())
        self.doingWidget.setAlignment(Qt.AlignHCenter)
        splitter.addWidget(doingContainer)

        doneContainer.setLayout(QVBoxLayout())
        doneContainer.layout().addWidget(customLabel("<h1>Done</h1>"))
        doneContainer.layout().addWidget(self.doneWidget)
        self.doneWidget.setWidget(QWidget())
        self.doneWidget.widget().setLayout(QGridLayout())
        self.doneWidget.setAlignment(Qt.AlignHCenter)
        splitter.addWidget(doneContainer)

        self.centralWidget.setLayout(QVBoxLayout())
        self.centralWidget.layout().addWidget(self.projectName)
        self.centralWidget.layout().addWidget(splitter)
        self.setCentralWidget(self.centralWidget)

    def loadProjects(self):
        lsProjects = self.database.getProjects()
        menuProject = QMenu("", self)
        self.menuRescent.clear()
        for project in lsProjects:
            actionRessent = QAction(project["name"], self)
            actionRessent.setObjectName("{}".format(project["id"]))
            self.menuRescent.addAction(actionRessent)
            menuProject.addAction(actionRessent)
            actionRessent.triggered.connect(self.loadTasks)
        self.btnAllProject.setMenu(menuProject)

    def loadTasks(self):
        projectId = self.sender().objectName()
        if len(projectId) == 0:
            projectId = self.currentProject["id"]
        lsTasks = self.database.getTasks(projectId)
        lsProjects = self.database.getProjects(projectId)
        if len(lsProjects) == 0:
            return
        self.currentProject = lsProjects[0]
        self.projectName.setText(lsProjects[0]["name"])
        self.projectName.setAlignment(Qt.AlignCenter)
        layoutToDo, layoutDoing, layoutDone = QGridLayout(), QGridLayout(), QGridLayout()
        widgetToDo, widgetDoing, widgetDone = QWidget(self), QWidget(), QWidget()

        for task in lsTasks:
            labelTask = TaskWidget(task["description"], self.database, task)
            labelTask.setStyleSheet("border: 2px solid #009688; border-radius: 10px")
            labelTask.setMaximumHeight(70)
            labelTask.setAlignment(Qt.AlignCenter)
            labelTask.signals.stateChanged.connect(self.testFct)
            if task["state"] == 1:
                layoutToDo.addWidget(labelTask)
            elif task["state"] == 2:
                layoutDoing.addWidget(labelTask)
            else:
                layoutDone.addWidget(labelTask)

        widgetToDo.setLayout(layoutToDo)
        widgetDoing.setLayout(layoutDoing)
        widgetDone.setLayout(layoutDone)

        widgetToDo.setStyleSheet(
            "QWidget{background-color: toDobg} TaskWidget{background-color: white}".replace("toDobg", toDoBackground))
        widgetDoing.setStyleSheet(
            "QWidget{background-color: toDobg} TaskWidget{background-color: white}".replace("toDobg", doingBackground))
        widgetDone.setStyleSheet(
            "QWidget{background-color: toDobg} TaskWidget{background-color: white}".replace("toDobg", doneBackground))

        self.toDoWidget.setWidget(widgetToDo)
        self.doingWidget.setWidget(widgetDoing)
        self.doneWidget.setWidget(widgetDone)

        if len(lsTasks) > 0:
            taskTodo, doingTask, doneTask = "{}".format((layoutToDo.count() / len(lsTasks) * 100))[:4], \
                                            "{}".format((layoutDoing.count() / len(lsTasks) * 100))[:4], \
                                            "{}".format((layoutDone.count() / len(lsTasks)) * 100)[:4]
            self.labelStatistic.setText(
                f"<div style='text-align: center'><span style='background-color:{toDoBackground}'>{taskTodo}% To do\t</span>"
                f"<span style='background-color:{doingBackground}'>{doingTask}% Doing\t</span>"
                f"<span style='background-color:{doneBackground}'>{doneTask}% Done</span></div>")
            self.labelStatistic.setAlignment(Qt.AlignRight)
        else:
            self.labelStatistic.setText("")
        self.actionNewTask.setEnabled(self.currentProject is not None)
        self.actionCloseProject.setEnabled(self.currentProject is not None)
        self.actionDeleteProject.setEnabled(self.currentProject is not None)
        self.menuExport.setEnabled(len(lsTasks) > 0)
        self.actionRenameProject.setEnabled(self.currentProject is not None)

    def onCreateNewProject(self):
        projectName = QInputDialog.getText(self, "New project", "Enter the project's name")[0]
        if len(projectName) != 0:
            idProject = self.database.addProject(projectName)
            self.currentProject = self.database.getProjects(idProject)[
                0] if idProject is not None else self.currentProject
            self.loadProjects()
            self.loadTasks()

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        menu = QMenu()
        menu.addAction(self.actionNewTask)
        menu.addSeparator()
        menu.addAction(self.actionImportProject)
        menu.addSeparator()
        menu.addAction(self.actionRenameProject)
        menu.addAction(self.actionCloseProject)
        menu.addAction(self.actionDeleteProject)
        menu.addSeparator()
        menu.addMenu(self.menuExport)
        menu.exec(event.globalPos())

    def onAddTask(self):
        description = QInputDialog.getText(self, "", "Description")[0]
        if len(description) == 0:
            return
        idProject = self.currentProject["id"]
        self.database.addTask(description, idProject)
        self.loadTasks()

    def onDeleteProject(self):
        response = QMessageBox.question(self, "", "Do  you want to delete the project: {} ?".format(
            self.projectName.toPlainText()))
        if response == QMessageBox.Yes:
            self.database.deleteProject(self.currentProject["id"])
            QMessageBox.information(self, "", "Project {} deleted".format(self.projectName.toPlainText()))
            self.onCloseProject()
            self.loadProjects()

    def onRenameProject(self):
        newName = QInputDialog.getMultiLineText(self, "Rename project", "New name", self.currentProject["name"])
        if not newName[1] or len(newName[0]) <= 0:
            return
        response = QMessageBox.question(self, "", "Do you want to rename {} to {}".format(
            self.projectName.toPlainText(), newName[0]))
        if response == QMessageBox.Yes:
            self.database.renameProject(self.currentProject["id"], newName[0])
            self.currentProject["name"] = newName[0]
            self.projectName.setText(newName[0])
            self.projectName.setAlignment(Qt.AlignHCenter)
            self.loadProjects()

    def testFct(self):
        print("Test fct")
        QTimer.singleShot(10, self.loadTasks)

    def createMenu(self):
        menuFile = QMenu("Project", self)

        menuFile.addAction(self.actionNewProject)
        self.actionNewProject.setShortcut(QKeySequence.New)
        menuFile.addAction(self.actionImportProject)
        self.actionImportProject.setShortcut(QKeySequence.Open)
        menuFile.addSeparator()
        menuFile.addMenu(self.menuRescent)

        self.menuExport.addAction("HTML").triggered.connect(self.onExportProjectAsHtml)
        self.menuExport.addAction("XML").triggered.connect(self.onExportProjectAsXml)
        self.menuExport.setEnabled(False)
        menuFile.addMenu(self.menuExport)

        menuFile.addMenu(self.menuExport)
        menuFile.addSeparator()

        menuFile.addAction(self.actionCloseProject)
        menuFile.addAction(self.actionRenameProject)
        menuFile.addAction(self.actionDeleteProject)
        self.actionDeleteProject.setEnabled(False)
        self.actionRenameProject.setEnabled(False)
        self.actionCloseProject.setEnabled(False)

        menuFile.addSeparator()
        actionQuit = menuFile.addAction("Quit")
        actionQuit.setShortcut(QKeySequence.Quit)
        actionQuit.triggered.connect(self.onQuit)
        self.menuBar().addMenu(menuFile)

        menuTask = QMenu("Task", self)
        menuTask.addAction(self.actionNewTask)
        self.actionNewTask.setEnabled(False)

        menuPreference = QMenu("Preferences", self)
        menuPreference.addAction("Font").triggered.connect(self.onChooseFont)
        menuPreference.addAction("Reset").triggered.connect(self.onResetPreference)

        self.menuBar().addMenu(menuTask)
        self.menuBar().addMenu(menuPreference)
        self.menuBar().addAction("About").triggered.connect(self.onShowAbout)

        self.actionNewTask.triggered.connect(self.onAddTask)
        self.actionNewProject.triggered.connect(self.onCreateNewProject)
        self.actionImportProject.triggered.connect(self.onImportProject)
        self.actionDeleteProject.triggered.connect(self.onDeleteProject)
        self.actionCloseProject.triggered.connect(self.onCloseProject)
        self.actionRenameProject.triggered.connect(self.onRenameProject)

    def createToolBar(self):
        self.toolBarFile.addAction(self.actionNewProject)
        self.toolBarFile.addAction(self.actionImportProject)
        self.toolBarFile.addSeparator()
        self.toolBarFile.addAction(self.actionNewTask)
        self.toolBarFile.addWidget(self.btnAllProject)
        self.btnAllProject.setFlat(True)
        self.btnAllProject.setMenu(QMenu(""))

    def onCloseProject(self):
        self.currentProject = None
        self.toDoWidget.setWidget(QWidget())
        self.doingWidget.setWidget(QWidget())
        self.doneWidget.setWidget(QWidget())
        self.projectName.setText("None Project")
        self.projectName.setAlignment(Qt.AlignHCenter)
        self.actionNewTask.setEnabled(False)
        self.actionCloseProject.setEnabled(False)
        self.actionDeleteProject.setEnabled(False)
        self.menuExport.setEnabled(False)
        self.actionRenameProject.setEnabled(False)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if not self.onQuit():
            event.ignore()

    def onQuit(self):
        response = QMessageBox.question(self, "", "Are you sure to quit ?")
        if response == QMessageBox.Yes:
            qApp.exit()
        return False

    def onImportProject(self):
        fileName = QFileDialog.getOpenFileName(self, "Import a project", os.getenv("HOME"), "*.xml")[0]
        if len(fileName) == 0:
            return
        domDocument = QDomDocument("My project")
        with open(fileName, "r") as file:
            domDocument.setContent(file.read())
        project = domDocument.documentElement()
        taskElement = project.firstChild()
        lsTask = []
        id = self.database.addProject(project.attribute("name", "eryct"))
        if id is None:
            return
        while not taskElement.isNull():
            if not taskElement.isElement():
                continue
            self.database.addTask(taskElement.toElement().text(), id, taskElement.toElement().attribute("state"))
            taskElement = taskElement.nextSibling()
        self.currentProject = self.database.getProjects(id)[0]
        self.loadProjects()
        self.loadTasks()

    def onExportProjectAsHtml(self):
        if self.currentProject is None:
            return
        toDoContent, doingContent, doneContent = "", "", ""
        lsTasks = self.database.getTasks(self.currentProject["id"])
        for task in lsTasks:
            if task["state"] == 1:
                toDoContent = f"{toDoContent}<div class='task'>{task['description']}</div>"
            elif task["state"] == 2:
                doingContent = f"{doingContent}<div class='task'>{task['description']}</div>"
            else:
                doneContent = f"{doingContent}<div class='task'>{task['description']}</div>"
        with open("template.html", "r") as file:
            htmlCode = file.read(2048).replace(":ProjectName", self.currentProject["name"]).replace(
                ":toDoContent", toDoContent).replace("doingContent", doingContent).replace(
                ":doneContent", doneContent)
            self.saveFile(htmlCode, "html")

    def onExportProjectAsXml(self):
        if self.currentProject is None:
            return
        lstask = self.database.getTasks(self.currentProject["id"])
        xmlCode = '<?xml version="1.0" encoding="UTF-8"?>\n<project name= ":projectName">:content</project>\n'
        tackCode = ""
        for task in lstask:
            tackCode = f"\t{tackCode}<task state='{task['state']}'>{task['description']}</task>\n"
        xmlCode = xmlCode.replace(":projectName", self.currentProject["name"]).replace(
            ":content", tackCode)
        self.saveFile(xmlCode, "xml")

    def saveFile(self, content: str, extension="html"):
        fileName = QFileDialog.getSaveFileName(self, "Save as xml file", os.getenv("HOME"), f"*.{extension}")[0]
        if len(fileName) == 0:
            return
        fileName = f"{fileName}.{extension}" if not fileName.endswith(f".{extension}") else fileName
        with open(f"{fileName}", "w") as newFile:
            newFile.write(content)
            QMessageBox.information(self, "", "Done!")

    def onChooseFont(self):
        fonts = QFont()
        font, ok = QFontDialog.getFont(QFont())
        if not ok:
            return
        pref = self.database.getPreferences()
        pref["fontSize"] = font.pointSize()
        pref["fontFamily"] = font.family()
        pref["fontStyle"] = font.style()
        qApp.setFont(font)
        self.database.setPreferences(pref)

    def onResetPreference(self):
        response = QMessageBox.question(self, "", "Reset the default preference ?")
        if response == QMessageBox.Yes:
            self.database.resetPreference()
            qApp.setFont(self.database.getPreferences()["font"])

    def onShowAbout(self):
        QMessageBox.information(self, "Project Manager",
                                "<div style='text-align:center'><div style='font-size:18px'>Project manager</div>"
                                "<div>Version 0.1</div>"
                                "<div style='font-style: italic;'>Provided by voidEtoile</div></div>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.resize(900, 500)
    mainWindow.show()
    sys.exit(app.exec())
