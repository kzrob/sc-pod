import definitions as defs
import amazon_stores as stores
import pandas as pd
import requests
import zipfile
import json
import os
import chardet
from sqlalchemy import create_engine

def detect_file_encoding(file: str, sample_size: int = 10000) -> str | None:
    with open(file, 'rb') as f:
        rawdata = f.read(sample_size)
    result = chardet.detect(rawdata)
    return result['encoding']


def tsv_to_df(tsv: str) -> pd.DataFrame:
    df = pd.read_csv(tsv, sep="\t", encoding=detect_file_encoding(tsv)) 
    df = df.dropna(axis=1, how="all")  # Drop columns that are completely empty
    return df


def download_and_extract_zip(url: str, folder: str) -> None:
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


def append_new_data(df: pd.DataFrame, i: int) -> None:
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
    asin = json_data["asin"]

    # Dispatch to the correct store handler.
    stores.process(asin, df, json_data, row_index)


def countOrders(df: pd.DataFrame) -> str | None:
    if "color" not in df.columns or "quantity-purchased" not in df.columns:
        return None
    
    map = {}
    for index, color in df["color"].items():
        quantity = int(df.loc[int(index), "quantity-purchased"])  # type: ignore[arg-type]
        color_key = str(color)
        map[color_key] = map.get(color_key, 0) + quantity
    map["Total"] = sum(map.values())

    output = ""
    for key, value in map.items():
        output += f"{key}: {value} | "
    
    return output


def main(tsv_path: str) -> str | None:
    df = tsv_to_df(tsv_path)

    for i in range(len(df)):
        append_new_data(df, i)

    engine = create_engine(f'sqlite:///{defs.DATABASE}')
    df.to_sql(name='products', con=engine, if_exists='replace', index=False)

    return countOrders(df)


# for debugging
if __name__ == '__main__':
    main(defs.TSV_PATH)