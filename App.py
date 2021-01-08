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
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts')
    data = cur.fetchall()
    return render_template('index.html', contacts=data)


# Page redirection section

@app.route('/department')
def redirect_department():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM department')
    data = cur.fetchall()
    return render_template('add-department.html', departments=data)


@app.route('/result')
def redirect_informationSearch():
    return render_template('result-search.html')


@app.route('/principal')
def redirect_searchSpecialization():
    return render_template('principal.html')


# Section of to insert in database

@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO contacts (fullname, phone, email) VALUES(%s, %s, %s)', (fullname, phone, email))
        mysql.connection.commit()
        flash('Contact Added Successfully')
        return redirect(url_for('Index'))


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


# Section of to update in database

@app.route('/edit/<id>')
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE id = %s', (id))
    data = cur.fetchall()
    return render_template('edit-contact.html', contact=data[0])


@app.route('/update/<id>', methods=['POST'])
def update_contact(id):
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE contacts
            SET fullname = %s,
                phone = %s,
                email = %s
            WHERE id = %s
        """, (fullname, phone, email, id))
        mysql.connection.commit()
        flash('Contact Updated Successfully')
        return redirect(url_for('Index'))


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


# Section of to delete in database

@app.route('/delete/<string:id>')
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('Index'))


@app.route('/delete_department/<string:id>')
def delete_department(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM department WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Department Removed Successfully')
    return redirect(url_for('redirect_department'))


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

    print(jsonify({'provinces': provinceArray}))
    return render_template('principal.html', provinces=provinces)


if __name__ == '__main__':
    app.run(port=3000, debug=True)
