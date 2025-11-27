import definitions as defs
import amazon_stores as stores
import pandas as pd
import requests
import zipfile
import json
import os
import chardet
from sqlalchemy import create_engine

def detect_file_encoding(file, sample_size=10000):
    with open(file, 'rb') as f:
        rawdata = f.read(sample_size)
    result = chardet.detect(rawdata)
    return result['encoding']


def download_and_extract_zip(url, folder):
    # download zip
    zip = folder + ".zip"
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for bad status codes

    # write to disk
    with open(zip, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # extract zip and remove when done
    with zipfile.ZipFile(zip, 'r') as zip_ref:
        zip_ref.extractall(folder)
    os.remove(zip)


def process_tsv(tsv):
    df = pd.read_csv(tsv, sep="\t", encoding=detect_file_encoding(tsv))  # Adjust encoding as needed
    df = df.dropna(axis=1, how="all")  # Drop columns that are completely empty
    return df


def append_new_data(df, i, store_name):
    id = df["order-item-id"][i]
    url = df["customized-url"][i]
    folder = os.path.join(defs.DOWNLOADS_DIR, str(id))

    if not os.path.isdir(folder):
        os.makedirs(defs.DOWNLOADS_DIR, exist_ok=True)
        download_and_extract_zip(url, folder)

        # Turn file.jpg into .jpg
        for entry_name in os.listdir(folder):
            if "." in entry_name:
                file_path = os.path.join(folder, entry_name)
                os.rename(file_path, os.path.join(folder, "." + file_path.split(".")[-1]))

    json_file = os.path.join(folder, ".json")
    with open(json_file, 'r') as jf:
        json_data = json.load(jf)

    row_index = df.index[i]

    # Dispatch to the correct store handler. Use a mapping to known handlers.
    STORE_HANDLERS = {
        'jubope_keychain': stores.jubope_keychain,
        'jubope_bracelet': stores.jubope_bracelet,
        'cdbuy_keychain': stores.cdbuy_keychain,
    }

    handler = STORE_HANDLERS.get(store_name)
    handler(df, json_data, row_index)



def main(input_path, store):
    if input_path is None:
        return None

    df = process_tsv(input_path)

    for i in range(len(df)):
        append_new_data(df, i, store)

    engine = create_engine(f'sqlite:///{defs.DATABASE}')
    df.to_sql(name='products', con=engine, if_exists='replace', index=False)
