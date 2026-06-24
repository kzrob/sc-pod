#!/usr/bin/env python3

import backend, config
from flask import Flask, render_template, url_for, redirect, request
from waitress import serve
import os

def mkdirs():
    os.makedirs(config.DOWNLOADS_DIR, exist_ok=True)
    os.makedirs(config.TSV_DIR, exist_ok=True)

def update_tsv_path() -> None:
    global tsv_path

    selected = request.form.get("tsv")
    if not selected:
        return

    selected_path = os.path.join(config.TSV_DIR, selected)
    tsv_path = selected_path

mkdirs()

tsv_path = None
tsv_list = [f for f in os.listdir(config.TSV_DIR) if f.endswith('.tsv')]

app = Flask(__name__, template_folder=config.TEMPLATES_DIR, static_folder=config.STATIC_DIR)
app.secret_key = "TODO: make this secret"


@app.route('/', methods=['GET', 'POST'])
def index():
    update_tsv_path()
    
    return render_template('index.html', tsv_list=tsv_list)


@app.route('/table', methods=['GET', 'POST'])
def table():
    update_tsv_path()
    print(tsv_path)
    
    values = {}
    for key in config.INPUT_VALUES:
        values[key] = request.form.get(key)
    
    df, count = backend.process_table(tsv_path, values)
    return render_template('table.html', tsv_list=tsv_list, df=df, count=count)


@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    update_tsv_path()
    
    df = backend.process_gallery(tsv_path)
    return render_template('gallery.html', tsv_list=tsv_list, df=df)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global tsv_path, tsv_list
    update_tsv_path()

    html = request.form.get("location", "index")
    mkdirs()

    if "file" not in request.files:
        return redirect(url_for(html))
    
    file = request.files['file']

    if file.filename == '':
        return redirect(url_for(html))
    
    path = os.path.join(config.TSV_DIR, file.filename)
    file.save(path)
    tsv_path = path
    tsv_list.append(os.path.basename(path))

    return redirect(url_for(html))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=config.PORT)
    # serve(app, host="0.0.0.0", port=config.PORT, threads=10)
