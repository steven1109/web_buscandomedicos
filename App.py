from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
from utils import ConsultingBD, BD
import math
import unicodedata

app = Flask(__name__)
# MySQL Connection localhost
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'buscando_medicos'
mysql = MySQL(app)
# Settings
app.secret_key = 'mysecretkey'


# Page redirection section
@app.route('/')
def redirect_heartweb():
    platform = request.user_agent.platform
    browser = request.user_agent.browser
    bdInfo = BD('m_log')
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO m_log ({}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(bdInfo.getColumnsTable()),
                (1, 'INICIO', '', '', '', '', '', '', '', platform, browser, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), None))
    mysql.connection.commit()

    uConsulting = ConsultingBD('department', 'S')
    return render_template('principal.html', departments=uConsulting.execQuery())


@app.route('/login')
def redirect_login():
    return render_template('login.html')


@app.route('/department')
def redirect_department():
    uConsulting = ConsultingBD('department', 'S')
    return render_template('add-department.html', departments=uConsulting.execQuery())


@app.route('/province')
def redirect_province():
    uConsulting = ConsultingBD('province', 'S')
    data = uConsulting.execQuery()

    uConsulting = ConsultingBD('department', 'S')
    dataDepartment = uConsulting.execQuery()
    return render_template('add-province.html', provinces=data, departments=dataDepartment)


@app.route('/district')
def redirect_district():
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT pr.cod_province, pr.t_name_province, pr.cod_department,
        dp.t_name_department, CONCAT(dp.t_name_department, ' -- ', pr.t_name_province) AS fullProvince
    FROM province AS pr
    INNER JOIN department AS dp ON pr.cod_department = dp.cod_department
    WHERE dp.n_active = 1 AND pr.n_active = 1
    ORDER BY dp.cod_department
    """)
    dataProvince = cur.fetchall()
    cur.execute("""
    SELECT ds.cod_district, ds.t_name_district, ds.n_active, ds.cod_province, pr.t_name_province
    FROM district AS ds
    INNER JOIN province AS pr ON ds.cod_province = pr.cod_province
    WHERE pr.n_active = 1 AND ds.n_active = 1
    ORDER BY pr.cod_province
    """)
    dataDistrict = cur.fetchall()
    return render_template('add-district.html', provinces=dataProvince, districts=dataDistrict)


@app.route('/result')
def redirect_informationSearch():
    return render_template('result-search.html')


@app.route('/search-specialty')
def redirect_search_specialty():
    return render_template('search-specialty.html')


@app.route('/search_specialization', methods=['POST'], defaults={'page': 1})
# @app.route('/search_specialization/<int:page>', methods=['POST', 'GET'])
def getSearchSpecialization(page):
    limit = 5
    # offset = page*limit - limit
    slDepartment = request.form.get('slDepartment')
    slProvince = request.form.get('slProvince')
    slDistrict = request.form.get('slDistrict')
    slGenero = request.form.get('slGenero')
    name_specialization = request.form.get('ipEspecializacion', None)
    dataObj = {}
    dataObj['genero'] = slGenero
    dataObj['departamento'] = slDepartment
    dataObj['provincia'] = slProvince
    dataObj['distrito'] = slDistrict
    form = ""

    slOrder = request.form.get('slOrder', None)
    orderby = "ORDER BY doc.t_lastname_doctor ASC"
    if slOrder is not None:
        form = "RESULTADO_BUSQUEDA"
        if int(slOrder) > 0:
            orderby = "ORDER BY prom DESC" if int(
                slOrder) == 1 else "ORDER BY prom ASC"
        else:
            orderby = "ORDER BY doc.t_lastname_doctor ASC"
    else:
        form = "PRINCIPAL"
        slOrder = 0

    filterStar = ""
    slFilterStar = request.form.get('slFilterStar', None)
    if slFilterStar is not None:
        form = "RESULTADO_BUSQUEDA"
        filterStar = f"HAVING prom >= {int(slFilterStar)}" if int(
            slFilterStar) > 0 else ""
    else:
        form = "PRINCIPAL"
        slFilterStar = 0

    cur = mysql.connection.cursor()

    # Pagination
    cur.execute('SELECT * FROM doctors WHERE n_active = 1')
    total_row = cur.rowcount
    total_page = math.ceil(total_row/limit)
    next_page = page + 1
    prev_page = page - 1
    # limit = "LIMIT {0} OFFSET {1}".format(limit, offset)

    # Ubigeo
    cur.execute('SELECT * FROM department WHERE n_active = 1')
    dataDepartment = cur.fetchall()
    slDepartment = 0 if slDepartment is None else slDepartment
    cur.execute(
        'SELECT * FROM province WHERE n_active = 1 and cod_department = {}'.format(slDepartment))
    dataProvince = cur.fetchall()
    slProvince = 0 if slProvince is None else slProvince
    cur.execute(
        'SELECT * FROM district WHERE n_active = 1 and cod_province = {}'.format(slProvince))
    dataDistrict = cur.fetchall()

    # Genero
    cur.execute('SELECT * FROM gender WHERE n_active = 1')
    dataGenero = cur.fetchall()

    # Condiciolanes
    clausulas = ""
    slGenero = 0 if slGenero is None else slGenero
    if int(slGenero) > 0:
        clausulas += ' AND doc.cod_gender_doctor = {}'.format(slGenero)

    if int(slDepartment) > 0:
        clausulas += ' AND doc.cod_office_department = {}'.format(slDepartment)

    if int(slProvince) > 0:
        clausulas += ' AND doc.cod_office_province = {}'.format(slProvince)

    slDistrict = 0 if slDistrict is None else slDistrict
    if int(slDistrict) > 0:
        clausulas += ' AND doc.cod_office_district = {}'.format(slDistrict)

    name_specialization = '' if name_specialization is None else name_specialization
    if len(name_specialization) > 0:
        name_specialization = unicodedata.normalize(
            'NFKD', name_specialization).encode('ASCII', 'ignore').upper().decode("utf-8")
        clausulas += ' AND sp.t_name_specialty LIKE "%{}%"'.format(
            name_specialization)

    query = 'SELECT doc.cod_doctor, ds.t_rne, sp.t_name_specialty, doc.t_name_doctor, doc.t_lastname_doctor, doc.t_dni_doctor,' \
        ' doc.cod_gender_doctor, doc.t_workphone_1_doctor,doc.t_workphone_2_doctor, doc.t_personalphone_doctor, doc.n_collegiate,' \
        ' doc.t_collegiate_code, doc.cod_office_department, doc.cod_office_province, doc.cod_office_district, doc.t_office_address,' \
        ' doc.t_professional_resume, doc.n_years_practicing, doc.n_attend_patients_covid, doc.n_attend_patients_vih, doc.t_current_job_title,' \
        ' COUNT(con.cod_doctor) AS count_doc, SUM(con.n_clasificacion) AS sum_com, ROUND(AVG(con.n_clasificacion),2) AS prom' \
        ' FROM doctors AS doc' \
        ' INNER JOIN doctor_specialty ds ON doc.cod_doctor = ds.cod_doctor' \
        ' INNER JOIN especialidad sp ON ds.cod_specialty = sp.cod_specialty' \
        ' INNER JOIN comentario AS con ON doc.cod_doctor = con.cod_doctor' \
        ' WHERE doc.n_active = 1 AND sp.n_active = 1 {0}' \
        ' GROUP BY doc.cod_doctor, ds.t_rne, sp.t_name_specialty, doc.t_name_doctor, doc.t_lastname_doctor, doc.t_dni_doctor,' \
        ' doc.cod_gender_doctor, doc.t_workphone_1_doctor,doc.t_workphone_2_doctor, doc.t_personalphone_doctor, doc.n_collegiate,' \
        ' doc.t_collegiate_code, doc.cod_office_department, doc.cod_office_province, doc.cod_office_district, doc.t_office_address,' \
        ' doc.t_professional_resume, doc.n_years_practicing, doc.n_attend_patients_covid, doc.n_attend_patients_vih, doc.t_current_job_title' \
        ' {1}' \
        ' {2}'.format(clausulas, filterStar, orderby)
    # ' {3}'.format(clausulas, filterStar, orderby, limit)

    cur.execute(query)
    dataDoctors = cur.fetchall()
    rows_affected = cur.rowcount

    platform = request.user_agent.platform
    browser = request.user_agent.browser
    cur.execute('''
    INSERT INTO m_log (n_tipo,t_formulario,t_especialidad_buscada,t_genero,t_departamento,
    t_provincia,t_distrito,t_medico_buscado,t_cita_inconclusa,t_platform,t_browser,d_creation_date) 
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (1, form, name_specialization, slGenero, slDepartment, slProvince, slDistrict, '', '',
          platform, browser, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    mysql.connection.commit()

    return render_template('search-specialty.html', data=dataObj, departments=dataDepartment, provinces=dataProvince, districts=dataDistrict,
                           generos=dataGenero, doctors=dataDoctors, valueSpecialty=name_specialization, dataOrder=slOrder, dataStar=slFilterStar,
                           rows_affected=rows_affected, pages=total_page, next=next_page, prev=prev_page, actual_page=page)


@app.route('/doctor')
def redirect_doctor():
    uConsulting = ConsultingBD('department', 'S')
    dataDepartments = uConsulting.execQuery()
    uConsulting = ConsultingBD('especialidad', 'S')
    dataEspecialidad = uConsulting.execQuery()
    return render_template('add-doctor.html', departments=dataDepartments, especialidades=dataEspecialidad)


@app.route('/specialization')
def redirect_specialization():
    uConsulting = ConsultingBD('especialidad', 'S')
    return render_template('add-specialization.html', specializations=uConsulting.execQuery())


# Section of to insert in database
@app.route('/add_specialization', methods=['POST'])
def add_specialization():
    if request.method == 'POST':
        name_specialization = request.form['specialization']
        if request.form.get('chbxActivo'):
            value = 1
        else:
            value = 0
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO especialidad (t_name_specialty, n_active, d_creation_date) VALUES(%s, %s, %s)',
                    (name_specialization, value, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        mysql.connection.commit()
        flash('Specialization Added Successfully')
        return redirect(url_for('redirect_specialization'))


@app.route('/add_department', methods=['POST'])
def add_department():
    if request.method == 'POST':
        if request.form.get('chbxActivo'):
            value = 1
        else:
            value = 0
        name_department = request.form['departamento']
        if len(name_department.strip()) == 0:
            flash('Campo departamento vacío')
        else:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO department (t_name_department, n_active, cod_country, d_creation_date) VALUES(%s, %s, %s, %s)',
                        (name_department, value, 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            mysql.connection.commit()
            flash('Departamento Added Successfully')

        return redirect(url_for('redirect_department'))


@app.route('/add_province', methods=['POST'])
def add_province():
    if request.method == 'POST':
        if request.form.get('chbxActivo'):
            value = 1
        else:
            value = 0
        name_province = request.form['province']
        slDepartment = request.form.get('slDepartment')
        if len(name_province.strip()) == 0:
            flash('Campo provincia vacío')
        elif int(slDepartment) == 0:
            flash('Debe seleccionar un Departamento')
        else:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO province (t_name_province, n_active, cod_department, d_creation_date) VALUES(%s, %s, %s, %s)',
                        (name_province, value, slDepartment, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            mysql.connection.commit()
            flash('Province Added Successfully')
        return redirect(url_for('redirect_province'))


@app.route('/add_district', methods=['POST'])
def add_district():
    if request.method == 'POST':
        if request.form.get('chbxActivo'):
            value = 1
        else:
            value = 0
        name_district = request.form['district']
        slProvince = request.form.get('slProvince')
        if len(name_district.strip()) == 0:
            flash('Campo distrito vacío')
        elif int(slProvince) == 0:
            flash('Debe seleccionar una Provincia')
        else:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO district (t_name_district, n_active, cod_province, d_creation_date) VALUES(%s, %s, %s, %s)',
                        (name_district, value, slProvince, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            mysql.connection.commit()
            flash('District Added Successfully')
        return redirect(url_for('redirect_district'))


@app.route('/add_doctors', methods=['POST','GET'])
def add_doctors():
    # if request.method == 'POST':
    namedoctor = request.form['namedoctor']
    lastnamedoctor = request.form['lastnamedoctor']
    dnidoctor = request.form['dnidoctor']
    phonework1 = request.form['workphonedoctor1']
    phonework2 = request.form['workphonedoctor2']
    phonepersonal = request.form['personalphonedoctor']
    slGenero = request.form.get('slGenero')
    slDepartment = request.form.get('slDepartment')
    slProvince = request.form.get('slProvince')
    slDistrict = request.form.get('slDistrict')
    addressdoctor = request.form['addressdoctor']
    collegiatecodedoctor = request.form['collegiatecodedoctor']
    slSpecialty1 = request.form.get('slSpecialty1')
    codermedoctor1 = request.form['codermedoctor1']
    slSpecialty2 = request.form.get('slSpecialty2')
    codermedoctor2 = request.form['codermedoctor2']
    slSpecialty3 = request.form.get('slSpecialty3')
    codermedoctor3 = request.form['codermedoctor3']
    slSpecialty4 = request.form.get('slSpecialty4')
    codermedoctor4 = request.form['codermedoctor4']
    slSpecialty5 = request.form.get('slSpecialty5')
    codermedoctor5 = request.form['codermedoctor5']

    if request.form.get('chbxColegiado'):
        value = 1
    else:
        value = 0

    columns = 't_name_doctor,t_lastname_doctor,t_dni_doctor,cod_gender_doctor,t_workphone_1_doctor,' \
        't_workphone_2_doctor,t_personalphone_doctor,n_collegiate,t_collegiate_code,cod_office_department,' \
        'cod_office_province,cod_office_district,t_office_address,n_uploaded_file,t_professional_resume,' \
        'n_years_practicing, n_attend_patients_covid, n_attend_patients_vih, t_link_facebook, t_link_instagram,' \
        't_link_linkedin,t_current_job_title,n_active,d_creation_date,d_modification_date'
    flash('District Added Successfully')

    return redirect(url_for('redirect_doctor'))


# Section of to update in database
@app.route('/edit_specialization/<id>')
def get_specialization(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM especialidad WHERE cod_specialty = {}'.format(id))
    data = cur.fetchall()
    return render_template('edit-specialization.html', specialization=data[0])


@app.route('/update_specialization/<id>', methods=['POST'])
def update_specialization(id):
    if request.method == 'POST':
        name_specialization = request.form['specialization']
        if request.form.get('chbxActivo'):
            value = 1
        else:
            value = 0
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE especialidad
            SET t_name_specialty = %s,
                n_active = %s,
                d_modification_date = %s
            WHERE cod_specialty = %s
        """, (name_specialization, value, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
        mysql.connection.commit()
        flash('Specialization Updated Successfully')
        return redirect(url_for('redirect_specialization'))


@app.route('/edit_department/<id>')
def get_department(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM department WHERE cod_department = %s', (id))
    data = cur.fetchall()
    return render_template('edit-department.html', department=data[0])


@app.route('/update_department/<id>', methods=['POST'])
def update_department(id):
    if request.method == 'POST':
        name_department = request.form['departamento']
        if request.form.get('chbxActivo'):
            value = 1
        else:
            value = 0
        if len(name_department.strip()) == 0:
            flash('El campo departamento no puede estar vacío')
            return redirect(f'/edit_department/{id}')
        else:
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE department
                SET t_name_department = %s,
                    n_active = %s,
                    d_modification_date = %s
                WHERE cod_department = %s
            """, (name_department, value, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
            mysql.connection.commit()
            flash('Department Updated Successfully')
            return redirect(url_for('redirect_department'))


@app.route('/edit_province/<string:id>')
def get_province(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM province WHERE cod_province = {0}'.format(id))
    data = cur.fetchall()
    # cur.execute('SELECT * FROM department WHERE id = {0}'.format(data[0][3]))
    cur.execute('SELECT * FROM department WHERE n_active = 1')
    dataDepartment = cur.fetchall()
    return render_template('edit-province.html', province=data[0], departments=dataDepartment)


@app.route('/update_province/<id>', methods=['POST'])
def update_province(id):
    if request.method == 'POST':
        name_province = request.form['province']
        slDepartment = request.form.get('slDepartment')
        if request.form.get('chbxActivo'):
            value = 1
        else:
            value = 0
        if len(name_province.strip()) == 0:
            flash('Campo provincia vacío')
            return redirect(f'/edit_province/{id}')
        elif int(slDepartment) == 0:
            flash('Debe seleccionar un Departamento')
            return redirect(f'/edit_province/{id}')
        else:
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE province
                SET t_name_province = %s,
                    n_active = %s,
                    cod_department = %s,
                    d_modification_date = %s
                WHERE cod_province = %s
            """, (name_province, value, slDepartment, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
            mysql.connection.commit()
            flash('Province Updated Successfully')
            return redirect(url_for('redirect_province'))


@app.route('/edit_district/<id>')
def get_district(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM district WHERE cod_district = {0}'.format(id))
    dataDistrict = cur.fetchall()
    cur.execute("""
    SELECT pr.cod_province, pr.t_name_province, pr.cod_department,
        dp.t_name_department, CONCAT(dp.t_name_department, ' -- ', pr.t_name_province) AS fullProvince
    FROM province AS pr
    INNER JOIN department AS dp ON pr.cod_department = dp.cod_department
    WHERE dp.n_active = 1
    ORDER BY dp.cod_department
    """)
    dataProvince = cur.fetchall()
    return render_template('edit-district.html', district=dataDistrict[0], provinces=dataProvince)


@app.route('/update_district/<id>', methods=['POST'])
def update_district(id):
    if request.method == 'POST':
        name_district = request.form['district']
        slProvince = request.form.get('slProvince')
        if request.form.get('chbxActivo'):
            value = 1
        else:
            value = 0

        if len(name_district.strip()) == 0:
            flash('Campo distrito vacío')
            return redirect(f'/edit_district/{id}')
        elif int(slProvince) == 0:
            flash('Debe seleccionar una Provincia')
            return redirect(f'/edit_district/{id}')
        else:
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE district
                SET t_name_district = %s,
                    n_active = %s,
                    cod_province = %s,
                    d_modification_date = %s
                WHERE cod_district = %s
            """, (name_district, value, slProvince, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
            mysql.connection.commit()
            flash('District Updated Successfully')
            return redirect(url_for('redirect_district'))

# Section of to delete in database
@app.route('/delete_specialization/<string:id>')
def delete_specialization(id):
    cur = mysql.connection.cursor()
    # cur.execute('DELETE FROM specialty WHERE cod_specialty = {0}'.format(id))
    cur.execute('UPDATE especialidad SET n_active = 0, d_modification_date = %s WHERE cod_specialty = %s',
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
    mysql.connection.commit()
    flash('Specialization Removed Successfully')
    return redirect(url_for('redirect_specialization'))


@app.route('/delete_department/<string:id>')
def delete_department(id):
    modification_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur = mysql.connection.cursor()
    # cur.execute('DELETE FROM department WHERE cod_department = {0}'.format(id))
    cur.execute('UPDATE department SET n_active = 0, d_modification_date = %s WHERE cod_department = %s',
                (modification_date, id))
    mysql.connection.commit()
    flash('Department Removed Successfully')
    return redirect(url_for('redirect_department'))


@app.route('/delete_province/<string:id>')
def delete_province(id):
    cur = mysql.connection.cursor()
    # cur.execute('DELETE FROM province WHERE cod_province = {0}'.format(id))
    cur.execute('UPDATE province SET n_active = 0, d_modification_date = %s WHERE cod_province = %s',
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
    mysql.connection.commit()
    flash('Province Removed Successfully')
    return redirect(url_for('redirect_province'))


@app.route('/delete_district/<string:id>')
def delete_district(id):
    cur = mysql.connection.cursor()
    # cur.execute('DELETE FROM district WHERE cod_district = {0}'.format(id))
    cur.execute('UPDATE district SET n_active = 0, d_modification_date = %s WHERE cod_district = %s',
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
    mysql.connection.commit()
    flash('District Removed Successfully')
    return redirect(url_for('redirect_district'))


# Section of to select in database
@app.route('/selectProvince/<id>')
def getProvinceByIdDepartment(id):
    uConsulting = ConsultingBD('province', 'SP', 'cod_department', id)
    # cur = mysql.connection.cursor()
    # cur.execute('SELECT * FROM province WHERE cod_department = %s', (id))
    # provinces = cur.fetchall()
    provinces = uConsulting.execQuery()
    provinceArray = []
    for province in provinces:
        provinceObj = {}
        provinceObj['id'] = province[0]
        provinceObj['name_province'] = province[1]
        provinceArray.append(provinceObj)

    return jsonify({'provinces': provinceArray})


@app.route('/selectDistrict/<int:id>')
def getDistrictByProvince(id):
    uConsulting = ConsultingBD('district', 'SP', 'cod_province', id)
    districts = uConsulting.execQuery()
    districtArray = []
    for district in districts:
        districtObj = {}
        districtObj['id'] = district[0]
        districtObj['name_district'] = district[1]
        districtArray.append(districtObj)

    return jsonify({'districts': districtArray})

@app.route('/allEspecialidades')
def getAllEspecialidades():
    uConsulting = ConsultingBD('especialidad', 'S')
    especialidades = uConsulting.execQuery()
    especialidadArray = []
    for especialidad in especialidades:
        especialidadObj = {}
        especialidadObj['id'] = especialidad[0]
        especialidadObj['name_especialidad'] = especialidad[1]
        especialidadArray.append(especialidadObj)

    return jsonify({'especialidades': especialidadArray})


if __name__ == '__main__':
    app.run(port=3000, debug=True)
