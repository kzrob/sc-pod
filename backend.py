from fileinput import filename
import pandas as pd
import requests
import zipfile
import json
import os
from sqlalchemy import create_engine

download_folder = "./files/"


def install(url, local_filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for bad status codes

    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def process_tsv(tsv_path):
    tsv_data = tsv_path
    os.makedirs(os.path.dirname(tsv_data) or '.', exist_ok=True)
    os.makedirs(download_folder, exist_ok=True)

    df = pd.read_csv(tsv_data, sep="\t", encoding="utf-16")  # Adjust encoding as needed
    df = df.dropna(axis=1, how="all")  # Drop columns that are completely empty

    def append_new_data(i):
        id = df["order-item-id"][i]
        folder = os.path.join(download_folder, str(id))
        file = os.path.join(download_folder, f"{id}.zip")

        install(df["customized-url"][i], file)
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(folder)

        # Normalize extracted filenames: move files to dot-prefixed names as previous logic assumed
        for entry_name in os.listdir(folder):
            if not "." in entry_name:
                continue
            file_path = os.path.join(folder, entry_name)
            try:
                os.rename(file_path, os.path.join(folder, "." + file_path.split(".")[-1]))
            except FileExistsError:
                pass

        json_file = os.path.join(folder, ".json")
        with open(json_file, 'r') as jf:
            data = json.load(jf)

        # Use the actual DataFrame index for assignment to avoid KeyError and chained-assignment
        row_idx = df.index[i]

        # These `.at` assignments will create the columns if they don't exist and set the value for the row
        areas = data["version3.0"]["customizationInfo"]["surfaces"][0]["areas"]
        df.at[row_idx, "color"] = areas[0].get("optionValue")
        df.at[row_idx, "engraving-side"] = areas[1].get("optionValue")
        df.at[row_idx, "logo-id"] = areas[2].get("optionValue")
        df.at[row_idx, "font-style"] = areas[3].get("fontFamily")
        df.at[row_idx, "side1"] = areas[3].get("text")
        if len(areas) > 5:
            df.at[row_idx, "fast-shipping"] = areas[5].get("optionValue")
            df.at[row_idx, "side2"] = areas[4].get("text")
        else:
            df.at[row_idx, "fast-shipping"] = areas[4].get("optionValue")

        try:
            os.remove(file)
        except OSError:
            pass

    for i in range(len(df)):
        append_new_data(i)

    engine = create_engine('sqlite:///data.db')
    df.to_sql(name='products', con=engine, if_exists='replace', index=False)


def main(input_path):
    if not input_path is None:
        process_tsv(input_path)
