import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import QSqlDatabase
import settings as st


class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)  # конструктор базового класса
        db = QSqlDatabase.addDatabase('QPSQL')  # QPSQL - тип подключеения postgressql
        db.setHostName(st.db_params['host'])
        db.setDatabaseName(st.db_params['dbname'])
        db.setPort(st.db_params['port'])
        db.setUserName(st.db_params['user'])
        db.setPassword(st.db_params['password'])
        db.open()
        #if ok:
        #    print('Connected to database', file=sys.stderr)
        #else:
        #    print('Connection FAILED', file=sys.stderr)