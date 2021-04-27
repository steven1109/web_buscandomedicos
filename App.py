from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
import datetime
from datetime import timedelta
from utils import ConsultingBD, BD
import os
import math
import unicodedata
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
ALLOWED_EXTENSIONS_PHOTO = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # max file 16MB
# MySQL Connection localhost
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'flaskuser'
app.config['MYSQL_PASSWORD'] = 'P@ssW0rd'
app.config['MYSQL_DB'] = 'buscando_medicos'
mysql = MySQL(app)
# Settings
app.secret_key = 'mysecretkey'
codi_depa = 0

# Page redirection section


@app.route('/')
def redirect_heartweb():
    platform = request.user_agent.platform
    browser = request.user_agent.browser
    bdInfo = BD('m_log')
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO m_log ({}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(bdInfo.getColumnsTable()),
                (1, 'INICIO', '', '', '', '', '', '', '', platform, browser, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), None))
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
        ' COUNT(con.cod_doctor) AS count_doc, ' \
        ' CASE WHEN COUNT(con.cod_doctor) > 0 THEN SUM(con.n_clasificacion) ELSE 0 END AS sum_com, ' \
        ' CASE WHEN COUNT(con.cod_doctor) > 0 THEN ROUND(AVG(con.n_clasificacion),2) ELSE 0 END AS prom' \
        ' FROM doctors AS doc' \
        ' INNER JOIN doctor_specialty ds ON doc.cod_doctor = ds.cod_doctor' \
        ' INNER JOIN especialidad sp ON ds.cod_specialty = sp.cod_specialty' \
        ' LEFT JOIN comentario AS con ON doc.cod_doctor = con.cod_doctor' \
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
          platform, browser, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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
    uConsulting = ConsultingBD('plans', 'S')
    dataPlanes = uConsulting.execQuery()
    return render_template('add-doctor.html', departments=dataDepartments, especialidades=dataEspecialidad, planes=dataPlanes)


@app.route('/view_doctor')
def redirect_viewdoctor():
    uConsulting = ConsultingBD('doctors', 'S')
    query = 'SELECT cod_doctor,t_name_doctor,t_lastname_doctor,t_dni_doctor,cod_gender_doctor,d_birthday, ' \
        'cod_born_department,cod_born_province,cod_born_district,t_workphone_1_doctor,t_workphone_2_doctor, ' \
        't_personalphone_doctor,n_collegiate,t_collegiate_code,cod_office_department,cod_office_province, ' \
        'cod_office_district,n_active FROM doctors where n_active = 1'
    return render_template('view-doctor.html', doctors=uConsulting.execQuery(query))


@app.route('/specialization')
def redirect_specialization():
    uConsulting = ConsultingBD('especialidad', 'S')
    return render_template('add-specialization.html', specializations=uConsulting.execQuery())


@app.route('/contact_us')
def redirect_contactus():
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d")

    uConsulting = ConsultingBD('especialidad', 'S')
    dataEspecialidades = uConsulting.execQuery()

    uConsulting = ConsultingBD('plans', 'S')
    dataPlanes = uConsulting.execQuery()

    start_hour = datetime.datetime.strptime("03:00", "%H:%M")
    hoursArray = []
    for i in range(1, (24 - int(start_hour.hour) + 1)):
        hoursObj = {}
        next_hour = start_hour + timedelta(hours=1)
        hoursObj['id'] = i
        hoursObj['value'] = start_hour.strftime(
            "%I:%M %p") + " - " + next_hour.strftime("%I:%M %p")
        hoursArray.append(hoursObj)
        start_hour = next_hour

    return render_template('contact-us.html', specializations=dataEspecialidades, currentdate=currentdate, planes=dataPlanes,
                           hours=hoursArray)


@app.route('/about_us')
def redirect_aboutus():
    return render_template('about-us.html')


@app.route('/medical_date/<id>')
def redirect_medical_date(id):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d")

    query = 'select doc.cod_doctor, doc.t_name_doctor, doc.t_lastname_doctor, ' \
            'doc.t_workphone_1_doctor, doc.cod_gender_doctor, gen.t_name_gender ' \
            'from doctors doc ' \
            'join gender gen on doc.cod_gender_doctor = gen.cod_gender ' \
            'where doc.n_active = 1 and doc.cod_doctor = {0};'.format(id)

    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()

    start_hour = datetime.datetime.strptime("03:00", "%H:%M")
    hoursArray = []
    for i in range(1, (24 - int(start_hour.hour) + 1)):
        hoursObj = {}
        next_hour = start_hour + timedelta(hours=1)
        hoursObj['id'] = i
        hoursObj['value'] = start_hour.strftime(
            "%I:%M %p") + " - " + next_hour.strftime("%I:%M %p")
        hoursArray.append(hoursObj)
        start_hour = next_hour

    return render_template('book-appointment.html', currentdate=currentdate, hours=hoursArray, doctor=data[0])


@app.route('/more_information/<id>')
def redirect_more_information(id):
    return render_template('more-information.html', id_doctor=id)


# @app.route('/sign_in', methods=['POST'])
# def redirect_admin():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         print(username, password)
#         return render_template('dashboard/index.html')
@app.route('/sign_in', methods=['GET', 'POST'])
def redirect_admin():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return render_template('dashboard/index.html')
    # return render_template('login.html', error=error)
    return redirect(url_for('redirect_login'))


@app.route('/admin_panel')
def redirect_admin_panel():
    return render_template('dashboard/index.html')


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
                    (name_specialization, value, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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
                        (name_department, value, 1, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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
                        (name_province, value, slDepartment, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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
                        (name_district, value, slProvince, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            mysql.connection.commit()
            flash('District Added Successfully')
        return redirect(url_for('redirect_district'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_filephoto(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_PHOTO


@app.route('/add_doctors', methods=['POST'])
def add_doctors():
    if request.method == 'POST':
        namedoctor = request.form['namedoctor']
        lastnamedoctor = request.form['lastnamedoctor']
        dnidoctor = request.form['dnidoctor']
        slGenero = request.form.get('slGenero')
        fecha = request.form['birthday']
        birthday = datetime.datetime.strptime(fecha, '%Y-%m-%d')
        slDepartmentBorn = request.form.get('slDepartmentBorn')
        slProvinceBorn = request.form.get('slProvinceBorn')
        slDistrictBorn = request.form.get('slDistrictBorn')
        phonework1 = request.form['workphonedoctor1']
        phonework2 = request.form['workphonedoctor2']
        phonepersonal = request.form['personalphonedoctor']
        slDepartment = request.form.get('slDepartment')
        slProvince = request.form.get('slProvince')
        slDistrict = request.form.get('slDistrict')
        addressdoctor = request.form['addressdoctor']
        valueColegiado = 1 if request.form.get('chbxColegiado') else 0
        collegiatecodedoctor = request.form.get('collegiatecodedoctor', None)
        valueCovid = 1 if request.form.get('chbxCovid') else 0
        valueVih = 1 if request.form.get('chbxVih') else 0
        valueLaborSocial = 1 if request.form.get('chbxLaborSocial') else 0
        slYear = request.form.get('slYear')
        currentjobdoctor = request.form['currentjobdoctor']
        slSpecialty1 = request.form.get('slSpecialty1')
        codermedoctor1 = request.form['codermedoctor1']
        linkFace = request.form['linkFace']
        linkInstagram = request.form['linkInstagram']
        linkLinkedin = request.form['linkLinkedin']
        cvdoctor = request.files['cvdoctor']
        photodoctor = request.files['photodoctor']
        resumeProfessional = request.form['resumeProfessional']
        valueCV = 0
        slPlan = request.form.get('slPlan')

        if cvdoctor.filename == '':
            flash('No ha cargado su CV, campo vacío')
            return redirect(url_for('redirect_doctor'))

        if cvdoctor and allowed_file(cvdoctor.filename):
            filenamecv = secure_filename(cvdoctor.filename)
            # cvdoctor.save(os.path.join(app.config['UPLOAD_FOLDER'], filenamecv))
            valueCV = 1

        if photodoctor and allowed_filephoto(photodoctor.filename):
            filenamephoto = secure_filename(photodoctor.filename)
            # photodoctor.save(os.path.join(app.config['UPLOAD_FOLDER'], filenamephoto))

        columnsDoctors = 't_name_doctor,t_lastname_doctor,t_dni_doctor,cod_gender_doctor,d_birthday, ' \
            'cod_born_department,cod_born_province,cod_born_district,t_workphone_1_doctor,t_workphone_2_doctor, ' \
            't_personalphone_doctor,n_collegiate,t_collegiate_code,cod_office_department,cod_office_province, ' \
            'cod_office_district,t_office_address,n_uploaded_file,t_name_filecv,t_name_photo,t_professional_resume, ' \
            'n_years_practicing,n_attend_patients_covid,n_attend_patients_vih,n_labor_social,t_link_facebook,t_link_instagram, ' \
            't_link_linkedin,t_current_job_title,n_active,d_creation_date,d_modification_date'
        columnsSpecialty = 't_rne,cod_specialty,cod_doctor,d_creation_date,d_modification_date'
        columnsPlanes = 'cod_plan,cod_doctor,n_active,d_creation_date'

        date_insert = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lenDoctor = len(columnsDoctors.split(','))
        args_doctors = ("("+",".join(["%s"]*lenDoctor)+")")
        cur = mysql.connection.cursor()
        queryInsertDoctor = f"""INSERT INTO doctors ({columnsDoctors}) VALUES {args_doctors}"""
        valueDoctor = (namedoctor, lastnamedoctor, dnidoctor, slGenero, birthday, slDepartmentBorn, slProvinceBorn, slDistrictBorn,
                       phonework1, phonework2, phonepersonal, valueColegiado, collegiatecodedoctor, slDepartment, slProvince, slDistrict,
                       addressdoctor, valueCV, filenamecv, filenamephoto, resumeProfessional, slYear, valueCovid, valueVih, valueLaborSocial,
                       linkFace, linkInstagram, linkLinkedin, currentjobdoctor, 2, date_insert, None)
        cur.execute(queryInsertDoctor, valueDoctor)
        mysql.connection.commit()

        lastDoctorId = cur.execute('select last_insert_id() from doctors')
        # Data doctors specialty
        values = []
        if int(slSpecialty1) > 0:
            values.append((codermedoctor1, slSpecialty1,
                           lastDoctorId, date_insert, None))

        lens = len(values[0])
        args_str = ("("+",".join(["%s"]*lens)+")")
        queryInsertDetalleDoctor = f"""INSERT INTO doctor_specialty ({columnsSpecialty}) VALUES {args_str}"""
        cur.executemany(queryInsertDetalleDoctor, values)

        lenPlan = len(columnsPlanes.split(','))
        args_plans = ("("+",".join(["%s"]*lenPlan)+")")
        queryInsertDetalleplandoctor = f"""INSERT INTO plan_doctor ({columnsPlanes}) VALUES {args_plans}"""
        valuesPlan = (int(slPlan), lastDoctorId, 1, date_insert)
        cur.execute(queryInsertDetalleplandoctor, valuesPlan)

        # Datos usuario
        emaildoctor = request.form['emaildoctor']
        passworddoctor = request.form['passworddoctor']
        columnsUser = 't_name_user,t_password_user,cod_profile,d_creation_date'
        lenUser = len(columnsUser.split(','))
        args_user = ("("+",".join(["%s"]*lenUser)+")")
        queryInsertUserDoctor = f"""INSERT INTO users ({columnsUser}) VALUES {args_user}"""
        cur.execute(queryInsertUserDoctor,
                    (emaildoctor, passworddoctor, 2, date_insert))
        mysql.connection.commit()

        flash('Doctor Added Successfully')
        return redirect(url_for('redirect_doctor'))


@app.route('/add_contactus', methods=['POST'])
def add_contactus():
    if request.method == 'POST':
        fullname = request.form['fullname']
        birthday = request.form['birthday']
        gender = request.form.get('rdGenero', '0')
        phone = request.form['phone']
        email = request.form['email']
        slSpecialty = request.form['slSpecialty']
        question = request.form['question']
        contact_time = request.form['contact_time']
        plan = request.form['plan']
        value = True

        if not fullname:
            value = False
            flash("Nombre y Apellido vacío")
        elif not birthday:
            value = False
            flash("Fecha de nacimiento vacío")
        elif gender == '0':
            value = False
            flash("Error, no ha seleccionado su genero")
        elif not phone:
            value = False
            flash("Teléfono vacío")
        elif not email:
            value = False
            flash("Correo Electrónico vacío")
        elif slSpecialty == "0":
            value = False
            flash("Error, debe seleccionar una especialidad")

        if not value:
            return render_template('contact-us.html', form=request.form)

        date_insert = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        columns = "t_fullname,d_birthday,n_gender,n_phone,t_email,cod_specialty,t_your_question,t_contact_time,cod_plan,d_creation_date"
        arg = ','.join('%s' for v in columns.split(','))
        cur = mysql.connection.cursor()
        statement = f"INSERT INTO contactus ({columns}) VALUES ({arg})"
        values = (fullname, birthday, gender, phone, email,
                  slSpecialty, question, contact_time, plan, date_insert)
        # cur.execute(statement, values)
        # mysql.connection.commit()
        flash('Specialization Updated Successfully')
        return redirect(url_for('redirect_contactus'))


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
        """, (name_specialization, value, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
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
            """, (name_department, value, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
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
            """, (name_province, value, slDepartment, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
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
            """, (name_district, value, slProvince, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
            mysql.connection.commit()
            flash('District Updated Successfully')
            return redirect(url_for('redirect_district'))


@app.route('/edit_doctor/<id>')
def get_doctor(id):
    query = 'SELECT doc.cod_doctor, doc.t_name_doctor, doc.t_lastname_doctor, doc.t_dni_doctor, doc.cod_gender_doctor, gen.t_name_gender,' \
        ' doc.d_birthday, doc.cod_born_department, doc.cod_born_province,doc.cod_born_district,' \
        ' doc.t_workphone_1_doctor,doc.t_workphone_2_doctor, ' \
        ' doc.t_personalphone_doctor, doc.n_collegiate, doc.t_collegiate_code, doc.cod_office_department, ' \
        ' doc.cod_office_province, doc.cod_office_district, doc.t_office_address, doc.t_professional_resume, ' \
        ' doc.n_years_practicing, doc.n_attend_patients_covid, doc.n_attend_patients_vih, doc.t_current_job_title,' \
        ' ds.t_rne, sp.cod_specialty, sp.t_name_specialty, doc.t_link_facebook,doc.t_link_instagram,doc.t_link_linkedin' \
        ' FROM doctors AS doc' \
        ' INNER JOIN doctor_specialty ds ON doc.cod_doctor = ds.cod_doctor' \
        ' INNER JOIN especialidad sp ON ds.cod_specialty = sp.cod_specialty' \
        ' INNER JOIN gender AS gen ON doc.cod_gender_doctor = gen.cod_gender' \
        ' WHERE doc.cod_doctor =  {0}'.format(id)

    uConsulting = ConsultingBD('doctors', 'S')
    data = uConsulting.execQuery(query)
    # Data of the place of birth
    uConsulting = ConsultingBD('department', 'S')
    dataDepartment = uConsulting.execQuery()
    uConsulting = ConsultingBD('province', 'SP', 'cod_department', data[0][7])
    dataProvince = uConsulting.execQuery()

    queryDis = f'select * from district where cod_department = {data[0][7]} and cod_province = {data[0][8]}'
    uConsulting = ConsultingBD('district', 'S')
    dataDistrict = uConsulting.execQuery(queryDis)
    print(queryDis)
    # Office location data
    uConsulting = ConsultingBD('department', 'S')
    dataDepartmentof = uConsulting.execQuery()
    uConsulting = ConsultingBD('province', 'SP', 'cod_department', data[0][15])
    dataProvinceof = uConsulting.execQuery()
    uConsulting = ConsultingBD('district', 'SP', 'cod_province', data[0][16])
    dataDistrictof = uConsulting.execQuery()

    uConsulting = ConsultingBD('especialidad', 'S')
    dataSpecialty = uConsulting.execQuery()

    return render_template('edit-doctor.html', doctors=data[0], departments=dataDepartment, provinces=dataProvince,
                           districts=dataDistrict, departmentsof=dataDepartmentof, provincesof=dataProvinceof,
                           districtsof=dataDistrictof, especialidades=dataSpecialty)


@app.route('/update_doctor/<id>', methods=['POST'])
def update_doctor(id):
    if request.method == 'POST':
        flash('Doctor Updated Successfully')
        return redirect(url_for('redirect_viewdoctor'))

# Section of to delete in database


@app.route('/delete_specialization/<string:id>')
def delete_specialization(id):
    cur = mysql.connection.cursor()
    # cur.execute('DELETE FROM specialty WHERE cod_specialty = {0}'.format(id))
    cur.execute('UPDATE especialidad SET n_active = 0, d_modification_date = %s WHERE cod_specialty = %s',
                (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
    mysql.connection.commit()
    flash('Specialization Removed Successfully')
    return redirect(url_for('redirect_specialization'))


@app.route('/delete_department/<string:id>')
def delete_department(id):
    modification_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
    mysql.connection.commit()
    flash('Province Removed Successfully')
    return redirect(url_for('redirect_province'))


@app.route('/delete_district/<string:id>')
def delete_district(id):
    cur = mysql.connection.cursor()
    # cur.execute('DELETE FROM district WHERE cod_district = {0}'.format(id))
    cur.execute('UPDATE district SET n_active = 0, d_modification_date = %s WHERE cod_district = %s',
                (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
    mysql.connection.commit()
    flash('District Removed Successfully')
    return redirect(url_for('redirect_district'))


# Section of to select in database


@app.route('/selectProvince/<id>')
def getProvinceByIdDepartment(id):
    codi_depa = id
    uConsulting = ConsultingBD('province', 'SP', 'cod_department', id)
    provinces = uConsulting.execQuery()
    provinceArray = []
    for province in provinces:
        provinceObj = {}
        provinceObj['id'] = province[1]
        provinceObj['name_province'] = province[2]
        provinceArray.append(provinceObj)

    return jsonify({'provinces': provinceArray})


@app.route('/selectDistrict/<int:id>/<int:depa>')
def getDistrictByProvince(id, depa):
    cur = mysql.connection.cursor()
    cur.execute(
        'select * from district where cod_department = %s and cod_province = %s', (depa, id))
    districts = cur.fetchall()
    # uConsulting = ConsultingBD('district', 'SP', 'cod_province', id)
    # districts = uConsulting.execQuery()
    districtArray = []
    for district in districts:
        districtObj = {}
        districtObj['id'] = district[1]
        districtObj['name_district'] = district[2]
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
