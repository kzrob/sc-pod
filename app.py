from flask import Flask, render_template, send_from_directory, g
import sqlite3 as sqlite

DATABASE = './data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite.connect(DATABASE)
        db.row_factory = sqlite.Row # To access columns by name
    return db


app = Flask(__name__)

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products ORDER BY `order-id` ASC")
    data = cursor.fetchall()
    return render_template('index.html', data=data)

@app.route('/images/<int:id>/<path:filename>')
def images(filename, id):
    return send_from_directory('files/' + str(id), filename)

if __name__ == '__main__':
    app.run(debug=True)
