from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from manager import Manager
from datetime import datetime
import sys

print(datetime.today())

app = QGuiApplication()
view = QQmlApplicationEngine()

manager = Manager()
view.rootContext().setContextProperty('manager',manager)

view.load('./view.qml')
app.exec_()
print("Application Closing")
manager.closing()