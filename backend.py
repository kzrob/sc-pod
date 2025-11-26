import pandas as pd
import requests
import zipfile
import json
import os
import chardet
from sqlalchemy import create_engine

download_folder = "./files/"

def detect_file_encoding(file, sample_size=100000):
    with open(file, 'rb') as f:
        rawdata = f.read(sample_size)
    result = chardet.detect(rawdata)
    return result['encoding']


def download_file(url, local_filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for bad status codes

    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def process_tsv(tsv_path):
    tsv_data = tsv_path
    os.makedirs(os.path.dirname(tsv_data) or '.', exist_ok=True)
    os.makedirs(download_folder, exist_ok=True)

    df = pd.read_csv(tsv_data, sep="\t", encoding=detect_file_encoding(tsv_data))  # Adjust encoding as needed
    df = df.dropna(axis=1, how="all")  # Drop columns that are completely empty
    return df


def add_jubope_data(df, json_data, i):
    row_idx = df.index[i]

    # These `.at` assignments will create the columns if they don't exist and set the value for the row
    areas = json_data["version3.0"]["customizationInfo"]["surfaces"][0]["areas"]
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


def append_new_data(df, i):
    id = df["order-item-id"][i]
    folder = os.path.join(download_folder, str(id))
    file = os.path.join(download_folder, f"{id}.zip")

    download_file(df["customized-url"][i], file)
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(folder)
    os.remove(file)

    # Normalize extracted filenames: move files to dot-prefixed names as previous logic assumed
    for entry_name in os.listdir(folder):
        if not "." in entry_name:
            continue
        file_path = os.path.join(folder, entry_name)
        os.rename(file_path, os.path.join(folder, "." + file_path.split(".")[-1]))

    json_file = os.path.join(folder, ".json")
    with open(json_file, 'r') as jf:
        json_data = json.load(jf)

    add_jubope_data(df, json_data, i)



def main(input_path):
    if input_path is None:
        return None
    
    df = process_tsv(input_path)

    for i in range(len(df)):
        append_new_data(df, i)

    engine = create_engine('sqlite:///data.db')
    df.to_sql(name='products', con=engine, if_exists='replace', index=False)