from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from config import Config


UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
ALLOWED_EXTENSIONS_PHOTO = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
# Settings
connection = mysql.connector.connect(database=Config.MYSQL_DB, user=Config.MYSQL_USER,
                                     password=Config.MYSQL_PASSWORD, host=Config.MYSQL_HOST)
cursor = connection.cursor()


@app.route("/")
def index():
    query = "select * from department"
    cursor.execute(query)
    data = cursor.fetchall()
    df = [val for val in data]
    print(df)
    return "Demo"


if __name__ == "__main__":
    app.run(port=3000, debug=True)
