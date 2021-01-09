from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL

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
    cur.execute('SELECT * FROM department')
    data = cur.fetchall()
    return render_template('add-department.html', departments=data)


@app.route('/province')
def redirect_province():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM province')
    data = cur.fetchall()

    cur.execute('SELECT * FROM department')
    dataDepartment = cur.fetchall()
    return render_template('add-province.html', provinces=data, departments=dataDepartment)


@app.route('/district')
def redirect_district():
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT pr.Id, pr.Name_province, pr.Id_deoartment,
        dp.Name_department, CONCAT(dp.Name_department, ' -- ', pr.Name_province) AS fullProvince
    FROM province as pr
    INNER JOIN department AS dp ON pr.Id_deoartment = dp.Id
    ORDER BY dp.Id
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
    SELECT ds.Id, ds.Name_district, ds.Active, ds.Id_province, pr.Name_province
    FROM district AS ds
    INNER JOIN province AS pr ON ds.Id_province = pr.Id
    ORDER BY pr.Id
    """)
    dataDistrict = cur.fetchall()
    return render_template('add-district.html', provinces=dataProvince, districts=dataDistrict)


@app.route('/result')
def redirect_informationSearch():
    return render_template('result-search.html')


@app.route('/doctor')
def redirect_doctor():
    return render_template('add-doctor.html')


@app.route('/principal')
def redirect_searchSpecialization():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM department')
    data = cur.fetchall()
    return render_template('principal.html', departments=data)


@app.route('/specialization')
def redirect_specialization():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM specializations')
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
        cur.execute('INSERT INTO specializations (Name_Specialization, Active) VALUES(%s, %s)', (name_specialization, value))
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
        cur.execute('INSERT INTO department (Name_department, Active) VALUES(%s, %s)', (name_department, value))
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
        cur.execute('INSERT INTO province (Name_province, Active, Id_deoartment) VALUES(%s, %s, %s)', 
        (name_province, value, slDepartment))
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
        cur.execute('INSERT INTO district (Name_district, Active, Id_province) VALUES(%s, %s, %s)', 
        (name_district, value, slProvince))
        mysql.connection.commit()
        flash('District Added Successfully')
        return redirect(url_for('redirect_district'))


# Section of to update in database

@app.route('/edit_specialization/<id>')
def get_specialization(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM specializations WHERE id = %s', (id))
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
            UPDATE specializations
            SET name_specialization = %s,
                Active = %s
            WHERE id = %s
        """, (name_specialization, value, id))
        mysql.connection.commit()
        flash('Specialization Updated Successfully')
        return redirect(url_for('redirect_specialization'))


@app.route('/edit_department/<id>')
def get_department(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM department WHERE id = %s', (id))
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
            SET Name_department = %s,
                Active = %s
            WHERE id = %s
        """, (name_department, value, id))
        mysql.connection.commit()
        flash('Department Updated Successfully')
        return redirect(url_for('redirect_department'))


@app.route('/edit_province/<string:id>')
def get_province(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM province WHERE id = {0}'.format(id))
    data = cur.fetchall()
    # cur.execute('SELECT * FROM department WHERE id = {0}'.format(data[0][3]))
    cur.execute('SELECT * FROM department')
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
            SET Name_province = %s,
                Active = %s,
                Id_deoartment = %s
            WHERE id = %s
        """, (name_province, value, slDepartment, id))
        mysql.connection.commit()
        flash('Province Updated Successfully')
        return redirect(url_for('redirect_province'))


@app.route('/edit_district/<id>')
def get_district(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM district WHERE id = {0}'.format(id))
    dataDistrict = cur.fetchall()
    cur.execute("""
    SELECT pr.Id, pr.Name_province, pr.Id_deoartment,
        dp.Name_department, CONCAT(dp.Name_department, ' -- ', pr.Name_province) AS fullProvince
    FROM province as pr
    INNER JOIN department AS dp ON pr.Id_deoartment = dp.Id
    ORDER BY dp.Id
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
            SET Name_district = %s,
                Active = %s,
                Id_province = %s
            WHERE id = %s
        """, (name_district, value, slProvince, id))
        mysql.connection.commit()
        flash('District Updated Successfully')
        return redirect(url_for('redirect_district'))

# Section of to delete in database

@app.route('/delete_specialization/<string:id>')
def delete_specialization(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM specializations WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Specialization Removed Successfully')
    return redirect(url_for('redirect_specialization'))


@app.route('/delete_department/<string:id>')
def delete_department(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM department WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Department Removed Successfully')
    return redirect(url_for('redirect_department'))


@app.route('/delete_province/<string:id>')
def delete_province(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM province WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Province Removed Successfully')
    return redirect(url_for('redirect_province'))


@app.route('/delete_district/<string:id>')
def delete_district(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM district WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('District Removed Successfully')
    return redirect(url_for('redirect_district'))


# Section of to select in database
@app.route('/selectProvince/<id>')
def getProvinceByIdDepartment(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM province WHERE Id_deoartment = %s', (id))
    provinces = cur.fetchall()
    provinceArray = []
    for province in provinces:
        provinceObj = {}
        provinceObj['id'] = province[0]
        provinceObj['name_province'] = province[1]
        provinceArray.append(provinceObj)

    return jsonify({'provinces': provinceArray})


@app.route('/selectDistrict/<id>')
def getDistrictByProvince(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM district WHERE Id_province = %s', (id))
    districts = cur.fetchall()
    districtArray = []
    for district in districts:
        districtObj = {}
        districtObj['id'] = district[0]
        districtObj['name_district'] = district[1]
        districtArray.append(districtObj)

    return jsonify({'districts': districtArray})


@app.route('/search_specialization', methods=['POST'])
def getSearchSpecialization():
    slDepartment = request.form.get('slDepartment')
    slProvince = request.form.get('slProvince')
    slDistrict = request.form.get('slDistrict')
    return (slDepartment+", "+slProvince+", "+slDistrict)

if __name__ == '__main__':
    app.run(port=3000, debug=True)
