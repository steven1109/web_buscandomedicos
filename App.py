from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
# MySQL Connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'buscando_medicos'
mysql = MySQL(app)
# Settings
app.secret_key = 'mysecretkey'


@app.route('/')
def Index():
    return redirect(url_for('redirect_searchSpecialization'))


# Page redirection section

@app.route('/department')
def redirect_department():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM department WHERE n_active = 1')
    data = cur.fetchall()
    return render_template('add-department.html', departments=data)


@app.route('/province')
def redirect_province():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM province WHERE n_active = 1')
    data = cur.fetchall()

    cur.execute('SELECT * FROM department WHERE n_active = 1')
    dataDepartment = cur.fetchall()
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
    # selectArray = []
    # for dp in dataProvince:
    #     dpObj = {}
    #     dpObj['id_province'] = dp[0]
    #     dpObj['id_department'] = dp[2]
    #     dpObj['name_department'] = dp[3]
    #     dpObj['name_province'] = dp[1]
    #     selectArray.append(dpObj)
    # print(selectArray)
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


@app.route('/search_specialization', methods=['POST'])
def getSearchSpecialization():
    slDepartment = request.form.get('slDepartment')
    slProvince = request.form.get('slProvince')
    slDistrict = request.form.get('slDistrict')
    slGenero = request.form.get('slGenero')
    name_specialization = request.form['ipEspecializacion']
    dataObj = {}
    dataObj['genero'] = slGenero
    dataObj['departamento'] = slDepartment
    dataObj['provincia'] = slProvince
    dataObj['distrito'] = slDistrict

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM department WHERE n_active = 1')
    dataDepartment = cur.fetchall()

    cur.execute(
        'SELECT * FROM province WHERE n_active = 1 and cod_department = {}'.format(slDepartment))
    dataProvince = cur.fetchall()

    cur.execute(
        'SELECT * FROM district WHERE n_active = 1 and cod_province = {}'.format(slProvince))
    dataDistrict = cur.fetchall()

    cur.execute('SELECT * FROM gender WHERE n_active = 1')
    dataGenero = cur.fetchall()

    clausulas = ""

    if int(slGenero) > 0:
        clausulas += ' AND doc.cod_gender_doctor = {}'.format(slGenero)

    if int(slDepartment) > 0:
        clausulas += ' AND doc.cod_office_department = {}'.format(slDepartment)

    if int(slProvince) > 0:
        clausulas += ' AND doc.cod_office_province = {}'.format(slProvince)

    if int(slDistrict) > 0:
        clausulas += ' AND doc.cod_office_district = {}'.format(slDistrict)
    
    if len(name_specialization) > 0:
        clausulas += ' AND sp.t_name_specialty LIKE "%{}%"'.format(name_specialization)
        cur.execute('SELECT * FROM specialty WHERE t_name_specialty LIKE "%{}%"'.format(name_specialization))
        dataSpecialty = cur.fetchall()
        print(dataSpecialty)

    query = 'SELECT doc.cod_doctor, ds.t_rne, sp.t_name_specialty, doc.t_name_doctor, doc.t_lastname_doctor, doc.t_dni_doctor,' \
        ' doc.cod_gender_doctor, doc.t_workphone_1_doctor,doc.t_workphone_2_doctor, doc.t_personalphone_doctor, doc.n_collegiate,' \
        ' doc.t_collegiate_code, doc.cod_office_department, doc.cod_office_province, doc.cod_office_district, doc.t_office_address,' \
        ' doc.t_professional_resume, doc.n_years_practicing, doc.n_attend_patients_covid, doc.n_attend_patients_vih, doc.t_current_job_title' \
        ' FROM doctors doc' \
        ' INNER JOIN doctor_specialty ds ON doc.cod_doctor = ds.cod_doctor' \
        ' INNER JOIN specialty sp ON ds.cod_specialty = sp.cod_specialty' \
        ' WHERE doc.n_active = 1 AND sp.n_active = 1 {}'.format(clausulas)

    cur.execute(query)
    dataDoctors = cur.fetchall()

    return render_template('search-specialty.html', data=dataObj, departments=dataDepartment, provinces=dataProvince, districts=dataDistrict,
                           generos=dataGenero, doctors=dataDoctors, valueSpecialty=name_specialization)


@app.route('/doctor')
def redirect_doctor():
    return render_template('add-doctor.html')


@app.route('/principal')
def redirect_searchSpecialization():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM department WHERE n_active = 1')
    data = cur.fetchall()
    # print(cur.rowcount)
    return render_template('principal.html', departments=data)


@app.route('/specialization')
def redirect_specialization():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM specialty WHERE n_active = 1')
    data = cur.fetchall()
    return render_template('add-specialization.html', specializations=data)


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
        cur.execute('INSERT INTO specialty (t_name_specialty, n_active, d_creation_date) VALUES(%s, %s, %s)',
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
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO district (t_name_district, n_active, cod_province, d_creation_date) VALUES(%s, %s, %s, %s)',
                    (name_district, value, slProvince, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        mysql.connection.commit()
        flash('District Added Successfully')
        return redirect(url_for('redirect_district'))


# Section of to update in database

@app.route('/edit_specialization/<id>')
def get_specialization(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM specialty WHERE cod_specialty = %s', (id))
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
            UPDATE specialty
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
    cur.execute('UPDATE specialty SET n_active = 0, d_modification_date = %s WHERE cod_specialty = %s',
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
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM province WHERE cod_department = %s', (id))
    provinces = cur.fetchall()
    provinceArray = []
    for province in provinces:
        provinceObj = {}
        provinceObj['id'] = province[0]
        provinceObj['name_province'] = province[1]
        provinceArray.append(provinceObj)

    return jsonify({'provinces': provinceArray})


@app.route('/selectDistrict/<int:id>')
def getDistrictByProvince(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM district WHERE cod_province = {}'.format(id))
    districts = cur.fetchall()
    districtArray = []
    for district in districts:
        districtObj = {}
        districtObj['id'] = district[0]
        districtObj['name_district'] = district[1]
        districtArray.append(districtObj)

    return jsonify({'districts': districtArray})


if __name__ == '__main__':
    app.run(port=3000, debug=True)
