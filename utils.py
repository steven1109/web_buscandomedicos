import MySQLdb
from datetime import datetime
from config import Config

# MySQL Connection localhost
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB = 'buscando_medicos'

db = MySQLdb.connect(host=Config.MYSQL_HOST,
                     database=Config.MYSQL_DB,
                     user=Config.MYSQL_USER,
                     password=Config.MYSQL_PASSWORD)


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
            query = "SELECT * FROM {0} WHERE {1} = {2}".format(
                self.table, self.column, self.codRow)
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


class BD:
    def __init__(self, tableName):
        self.tableName = tableName

    def getColumnsTable(self):
        bdSchema = {
            'm_log': 'n_tipo, t_formulario, t_especialidad_buscada, t_genero, t_departamento,'
                     't_provincia, t_distrito, t_medico_buscado, t_cita_inconclusa, t_platform, '
                     't_browser, d_creation_date, d_modification_date',
            'departments': 't_name_department, n_active, d_creation_date, d_modification_date, cod_country',
            'province': '',
            'district': '',
            'especialidad': '',
            'doctors': 't_name_doctor,t_lastname_doctor,t_dni_doctor,cod_gender_doctor,t_workphone_1_doctor,'
            't_workphone_2_doctor,t_personalphone_doctor,n_collegiate,t_collegiate_code,cod_office_department,'
            'cod_office_province,cod_office_district,t_office_address,n_uploaded_file,t_professional_resume,'
            'n_years_practicing,n_attend_patients_covid,n_attend_patients_vih,t_link_facebook,t_link_instagram,'
            't_link_linkedin,t_current_job_title,n_active,d_creation_date,d_modification_date'
        }

        return bdSchema[self.tableName]
