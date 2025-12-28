#!/usr/bin/env python3

import backend, config
from flask import Flask, render_template, url_for, redirect, request
from waitress import serve
import os

app = Flask(__name__, template_folder=config.TEMPLATES_DIR, static_folder=config.STATIC_DIR)
app.secret_key = "TODO: make this secret"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/table', methods=['GET', 'POST'])
def table():
    length = request.form.get("length")
    width = request.form.get("width")
    height = request.form.get("height")
    ounces = request.form.get("ounces")
    
    df, count = backend.process_table(config.TSV_PATH, length, width, height, ounces)
    return render_template('table.html', data=df, count=count)


@app.route('/gallery')
def gallery():
    df = backend.process_gallery(config.TSV_PATH)
    return render_template('gallery.html', data=df)


@app.route('/upload', methods=['POST'])
def upload():
    html = request.form.get("location", "index")
    os.makedirs(config.DOWNLOADS_DIR, exist_ok=True)

    if "file" not in request.files:
        return redirect(url_for(html))
    
    file = request.files['file']
    file.save(config.TSV_PATH)

    return redirect(url_for(html))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=config.PORT)
    # serve(app, host="0.0.0.0", port=config.PORT, threads=10)