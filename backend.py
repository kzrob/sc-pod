import definitions as defs
import pandas as pd
import requests
import zipfile
import json
import os
import chardet
from sqlalchemy import create_engine

def tsv_to_df(tsv: str, sample_size: int = 10000) -> pd.DataFrame:
    # Detect encoding
    with open(tsv, 'rb') as f:
        rawdata = f.read(sample_size)
    encoding = chardet.detect(rawdata)["encoding"]

    # Read TSV into DataFrame
    df = pd.read_csv(tsv, sep="\t", encoding=encoding) 
    df = df.dropna(axis=1, how="all")  # Drop columns that are completely empty
    return df


def download_and_extract_zip(url: str, folder: str) -> None:
    # Download zip
    zip = folder + ".zip"
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Write zip to disk
    with open(zip, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Extract zip into folder and remove when done
    with zipfile.ZipFile(zip, 'r') as zip_ref:
        zip_ref.extractall(folder)
    os.remove(zip)

    # Remove file names and only keep extensions
    for entry_name in os.listdir(folder):
        if "." in entry_name:
            file_path = os.path.join(folder, entry_name)
            os.rename(file_path, os.path.join(folder, "." + file_path.split(".")[-1]))


def append_new_data(df: pd.DataFrame, i: int) -> set:
    id = df["order-item-id"][i]
    url = df["customized-url"][i]
    folder = os.path.join(defs.DOWNLOADS_DIR, str(id))

    # Download zips
    if not os.path.isdir(folder):
        download_and_extract_zip(url, folder)

    json_file = os.path.join(folder, ".json")
    with open(json_file, 'r') as jf:
        json_data = json.load(jf)

    # Append data to DataFrame
    counters = set() # counting order properties
    row = df.index[i]
    
    df.at[i, "image"] = "/files/" + str(df.iloc[i]["order-item-id"]) + "/.jpg"

    surfaces = json_data["version3.0"]["customizationInfo"]["surfaces"]
    for i in surfaces: # for data
        areas = i["areas"]
        for area in areas:
            type = str(area.get("customizationType"))
            label = str(area.get("label"))
            if type == "Options":
                counters.add(label+" value")
                value = str.lower(area.get("optionValue"))
                if defs.MONTHS.get(value) is not None:
                    value = defs.MONTHS[value]
                df.at[row, label+" value"] = value
            elif type == "TextPrinting":
                df.at[row, label+" text"] = area.get("text")
                df.at[row, label+" font"] = area.get("fontFamily")
            else:
                defs.log(f"Unknown customization type: {type} for order-item-id: {id}")
    
    customizations = json_data["customizationData"]["children"][0]["children"][0]["children"]
    for custom in customizations: # for images
        type = str(custom.get("type"))
        if type == "OptionCustomization":
            image = custom["optionSelection"].get("thumbnailImage")
            if image is not None:
                df.at[row, label+" image"] = image.get("imageUrl")
        else:
            defs.log(f"Unknown customization type: {type} for order-item-id: {id}")
    
    return counters


# Counts a column's orders and returns a formatted string
def countOrders(df: pd.DataFrame, column: str, simple: bool = False) -> str | None:
    if simple and column in df.columns:
        return f"<b>{column} counts: {str(df[column].value_counts().index.size)}</b>"

    if column not in df.columns or "quantity-purchased" not in df.columns:
        defs.log(f"Cannot count orders for column: {column}")
        return None

    map = {}
    for index, value in df[column].items():
        if value == "" or pd.isna(value):
            continue
        quantity = df.loc[int(index), "quantity-purchased"]
        map[value] = map.get(value, 0) + int(quantity)
    map = dict(sorted(map.items()))
    map["Total"] = sum(map.values())

    output = f"<details><summary><b>{column} counts</b></summary><ul>"
    for key, value in map.items():
        output += f"<li>{key}: {value}</li>"
    output += "</ul></details>"

    return output


def main(tsv_path: str) -> dict[str | None]:
    if tsv_path is None or not os.path.exists(tsv_path):
        return None
    
    df = tsv_to_df(tsv_path)

    count = set()
    for i in range(len(df)):
        counters = append_new_data(df, i)
        if counters is not None:
            count = count.union(counters)

    engine = create_engine(f'sqlite:///{defs.DATABASE}')
    df.to_sql(name='products', con=engine, if_exists='replace', index=False)

    output = dict()
    output["orders"] = countOrders(df, "order-id", simple=True)
    for column in count:
        output[column] = countOrders(df, column)
    
    return output

# for debugging
if __name__ == '__main__':
    main(defs.TSV_PATH)