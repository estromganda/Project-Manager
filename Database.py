import random

from PyQt5.QtCore import QObject, QDir
from PyQt5.QtGui import QFont
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

databaseName = "data.sqlite"
home = QDir.home()

if not QDir(f"{home.absolutePath()}/.voidEtoile").exists():
    home.mkdir(".voidEtoile")
home.cd(".voidEtoile")

if not QDir(f"{home.absolutePath()}/.voidEtoile/projectManager").exists():
    home.mkdir("projectManager")
home.cd("projectManager")
databaseName = f"{home.absolutePath()}/{databaseName}"

print(databaseName)
# exit(0)

MLD = """
CREATE TABLE IF NOT EXISTS Project(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name VARCHAR(255),
	creationDate DATETIME DEFAULT NOW
);
CREATE TABLE IF NOT EXISTS Task(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	idProject INT UNSIGNED,
	description LONG TEXT,
	state INTEGER DEFAULT 1,
	FOREIGN KEY(idProject) REFERENCES Projects(id)
);
CREATE TABLE IF NOT EXISTS Preference(
	color VARCHAR(10),
	fontSize INTEGER,
	fontFamily VARCHAR(50),
	fontStyle VARCHAR(50)
);
"""


class Database(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.database = QSqlDatabase.addDatabase("QSQLITE", "Connection {}".format(random.random()))
        self.database.setDatabaseName(databaseName)
        if not self.database.open():
            print("Error at Database.__init__: {}".format(self.database.lastError().text()))
        self.createDatabase()

    def addProject(self, projectName: str):
        request = 'INSERT INTO Project(name)VALUES("{}");'.format(projectName)
        query = QSqlQuery(self.database)
        if not query.exec(request):
            print("Error at Database.addProject: {}".format(query.lastError().text()))
            print(request)
            return None
        return query.lastInsertId()

    def renameProject(self, idProject: int, projectName: str):
        query = "UPDATE Project SET name= '{}' WHERE id = `{}`".format(projectName, idProject)
        if not self.database.exec(query):
            print("Error at Database.renameProject: {}".format(self.database.lastError().text()))

    def getProjects(self, idProject=None, projectName=""):
        filter = ["name" if idProject is None else "id", projectName if idProject is None else idProject]
        request = "SELECT * FROM Project ORDER BY id DESC" if idProject is None and len(projectName) == 0 else \
            f"SELECT * FROM Project WHERE {filter[0]}='{filter[1]}' ORDER BY id DESC"
        query = QSqlQuery(self.database)
        lsProject = []
        if query.exec(request):
            while query.next():
                project = {"id": query.value("id"), "name": query.value("name"),
                           "creationDate": query.value("creationDate")}
                lsProject.append(project)
        else:
            print("Error at Database.getProjects: {}".format(query.lastError().text()))
        return lsProject

    def deleteProject(self, idProject: int):
        lsTables = ["Task", "Project"]
        for tableName in lsTables:
            query = "DELETE FROM '{}' WHERE id = '{}'".format(tableName, idProject)
            if not self.database.exec(query):
                print("Error at Database.deleteProject: {}".format(self.database.lastError().text()))

    def addTask(self, description: str, idProject: int, state=1):
        query = "INSERT INTO Task(description, idProject, state)" \
                "VALUES('{}', '{}', '{}')".format(description, idProject, state)
        if not self.database.exec(query):
            print("Error at Database.addTask: {}".format(self.database.lastError().text()))

    def getTasks(self, idProject: int):
        query = QSqlQuery(self.database)
        query.prepare("SELECT * FROM Task WHERE idProject = :idProject")
        query.bindValue(":idProject", idProject)
        lsTask = []
        if query.exec_():
            while query.next():
                task = {"id": query.value("id"), "description": query.value("description"),
                        "idProject": query.value("idProject"), "state": query.value("state")}
                lsTask.append(task)
        else:
            print("Error at Database.getProjects: {}".format(query.lastError().text()))
        return lsTask

    def updateTask(self, idTask: int, newDescription: str, newState: str):
        query = "UPDATE Task SET description= '{}', state= '{}' WHERE id = '{}'".format(
            newDescription, newState, idTask
        )
        if not self.database.exec(query):
            print("Error at Database.updateTask: {}".format(self.database.lastError().text()))

    def deleteTask(self, idTask: int):
        query = "DELETE FROM Task WHERE id = '{}'".format(idTask)
        if not self.database.exec(query):
            print("Error at Database.deleteTask: {}".format(self.database.lastError().text()))

    def createDatabase(self):
        query = QSqlQuery(self.database)
        lsRequests = MLD.split(";")
        for request in lsRequests:
            if request == "\n":
                continue
            if not query.exec(request):
                print("Error at Database.createDatabase: {}:".format(query.lastError().text()))
        self.initPreference()

    def getPreferences(self):
        query = QSqlQuery(self.database)
        if query.exec(f"SELECT * FROM Preference"):
            while query.next():
                pref = {"color": query.value("color"), "fontSize": query.value("fontSize"),
                        "fontFamily": query.value("fontFamily"), "fontStyle": query.value("fontStyle")}
                font = QFont(pref["fontFamily"], pref["fontSize"])
                font.setStyle(int(pref["fontStyle"]))
                pref["font"] = font

                return pref
        return []

    def setPreferences(self, pref):
        query = QSqlQuery(self.database)
        if not query.exec(f"UPDATE Preference SET color= '{pref['color']}', "
                          f"fontSize = '{pref['fontSize']}', fontFamily= '{pref['fontFamily']}',"
                          f"fontStyle = '{pref['fontStyle']}'"):
            print(f"Error at Database.setPreferences: {query.lastError().text()}")

    def initPreference(self, font: QFont = None):
        if len(self.getPreferences()) > 0:
            return
        if font is None:
            font = QFont("", 9)
        if not self.database.exec(f"INSERT INTO Preference(color, fontSize, fontFamily, fontStyle)"
                                  f"VALUES('#fff', '{font.pointSize()}', '{font.family()}', '{font.style()}')"):
            print(f"Error at Database.setPreferences: {self.database.lastError().text()}")

    def resetPreference(self):
        font = QFont("", 9)
        queries = ["DELETE FROM Preference",
                   f"INSERT INTO Preference(color, fontSize, fontFamily, fontStyle)"
                   f"VALUES('#fff', '{font.pointSize()}', '{font.family()}', '{font.style()}')"]
        for query in queries:
            if not self.database.exec(query):
                print(f"Error at Database.setPreferences: {self.database.lastError().text()}")

# db = Database()
# print(db.getPreferences())
