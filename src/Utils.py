import MySQLdb
from datetime import datetime

# MySQL Connection localhost
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB = 'buscando_medicos'

db = MySQLdb.connect(host=MYSQL_HOST,
                     database=MYSQL_DB,
                     user=MYSQL_USER,
                     password=MYSQL_PASSWORD)


class ConsultingBD:
    def __init__(self, table, type_consulting, column=None, codRow=None):
        self.table = table
        self.type_consulting = type_consulting
        self.query = None
        self.result = None
        self.column = column
        self.codRow = codRow

    def getQuery(self):
        query = ""
        if self.type_consulting == "S":
            query = "SELECT * FROM {0} WHERE n_active = 1".format(self.table)
        if self.type_consulting == "SP":
            query = "SELECT * FROM {0} WHERE {1} = {2}".format(self.table, self.column, self.codRow)
        if self.type_consulting == "DM":
            query = "UPDATE {0} SET n_active = 0, d_modification_date = {1} " \
                " WHERE {2} = {3};".format(
                    self.table, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.column, self.codRow)
        return query

    def execQuery(self):
        cur = db.cursor()
        cur.execute(self.getQuery())
        self.data = cur.fetchall()
        return self.data
