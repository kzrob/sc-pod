#!/usr/bin/env python3

import backend, config
from flask import Flask, render_template, url_for, send_from_directory, redirect, request
from waitress import serve

db_data = None
db_count = None

app = Flask(__name__, template_folder=config.TEMPLATES_DIR, static_folder=config.STATIC_DIR)

@app.route('/')
def index():
    return render_template('index.html', data=db_data, count=db_count)


@app.route('/upload', methods=['POST'])
def upload():
    if request.files["file"] is None:
        return redirect(url_for('index'))
    
    file = request.files['file']
    file.save(config.TSV_PATH)

    global db_data, db_count
    db_data, db_count = backend.main(config.TSV_PATH)

    print(db_data)
    
    return render_template('index.html', data=db_data, count=db_count)


@app.route('/files/<id>/<path:filename>')
def files(id, filename):
    return send_from_directory(f"{config.DOWNLOADS_DIR}/{id}", filename)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=config.PORT)
    # serve(app, host="0.0.0.0", port=app.config["PORT"], threads=10)