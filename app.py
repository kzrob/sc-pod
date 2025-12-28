#!/usr/bin/env python3

import backend, config
from flask import Flask, render_template, url_for, redirect, request
from waitress import serve
import os

os.makedirs(config.DOWNLOADS_DIR, exist_ok=True)
app = Flask(__name__, template_folder=config.TEMPLATES_DIR, static_folder=config.STATIC_DIR)
app.secret_key = "TODO: make this secret"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/table')
def table():
    data, count = backend.process_table(config.TSV_PATH)
    return render_template('table.html', data=data, count=count)


@app.route('/gallery')
def gallery():
    data = backend.process_gallery(config.TSV_PATH)
    return render_template('gallery.html', data=data)


@app.route('/upload', methods=['POST'])
def upload():
    html = request.form.get("location", "index")

    if "file" not in request.files:
        return redirect(url_for(html))
    
    file = request.files['file']
    file.save(config.TSV_PATH)

    return redirect(url_for(html))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=config.PORT)
    # serve(app, host="0.0.0.0", port=config.PORT, threads=10)