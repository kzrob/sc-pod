#!/usr/bin/env python3

import definitions as defs
from flask import Flask, render_template, url_for, send_from_directory, g, request, jsonify
from waitress import serve
import sqlite3 as sqlite
import os
import backend

os.makedirs(defs.DOWNLOADS_DIR, exist_ok=True)
app = Flask(__name__, template_folder=defs.TEMPLATES_DIR, static_folder=defs.STATIC_DIR)
app.config["PORT"] = 3001

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite.connect(defs.DATABASE)
        db.row_factory = sqlite.Row # To access columns by name
    return db

def get_data():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products ORDER BY `order-id` ASC")
    return cursor.fetchall()

db_count = None

@app.route('/')
def index():
    # If there's no DB file yet, show the upload UI
    if not os.path.exists(defs.DATABASE):
        return render_template('index.html', data=None)

    data = get_data()
    return render_template('index.html', data=data, count=db_count)


@app.route('/upload', methods=['POST'])
def upload():
    if request.files["file"] is None:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    file.save(defs.TSV_PATH)

    db_count = backend.main(defs.TSV_PATH)

    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        delattr(g, '_database')

    data = get_data()
    return render_template('index.html', data=data, count=db_count)


@app.route('/files/<id>/<path:filename>')
def files(id, filename):
	if id.isdigit():
		return send_from_directory(f"{defs.DOWNLOADS_DIR}/{id}", filename)
	return send_from_directory(f"{defs.IMAGES_DIR}/{id}", filename)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=app.config["PORT"])
    # serve(app, host="0.0.0.0", port=app.config["PORT"], threads=10)