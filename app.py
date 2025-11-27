import definitions as defs
from flask import Flask, render_template, send_from_directory, g, request, jsonify
from waitress import serve
import sqlite3 as sqlite
import os
import backend

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite.connect(defs.DATABASE)
        db.row_factory = sqlite.Row # To access columns by name
    return db


app = Flask(__name__, template_folder=defs.TEMPLATES_DIR, static_folder=defs.STATIC_DIR)

@app.route('/')
def index():
    # If there's no DB file yet, show the upload UI
    if not os.path.exists(defs.DATABASE):
        return render_template('index.html', data=None)

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM products ORDER BY `order-id` ASC")
        data = cursor.fetchall()
    except Exception:
        # table missing or other DB error — show upload UI
        return render_template('index.html', data=None)

    # If table exists but has no rows, show upload UI
    if not data:
        return render_template('index.html', data=None)

    return render_template('index.html', data=data)


@app.route('/upload', methods=['POST'])
def upload():
    # Accept a single file under form field 'file' and process it with backend
    if 'file' not in request.files:
        return jsonify({'error': 'no file provided'}), 400
    f = request.files['file']
    f.save(defs.TSV_PATH)

    try:
        backend.main(defs.TSV_PATH)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Close any cached DB connection so next request sees the new DB
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        delattr(g, '_database')

    return jsonify({'status': 'ok'})

@app.route('/files/<id>/<path:filename>')
def files(filename, id):
	if id.isdigit():
		return send_from_directory(f"{defs.DOWNLOADS_DIR}/{id}", filename)
	return send_from_directory(f"{defs.IMAGES_DIR}/{id}", filename)



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3001)
    # serve(app, host="0.0.0.0", port=3001, threads=10)