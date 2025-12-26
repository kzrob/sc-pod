import config
import pandas as pd
import requests
import zipfile
import json
import os
import chardet

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


def find_first_child(folder, extension: str) -> str | None:
    for entry_name in os.listdir(folder):
        if extension in entry_name:
            path = os.path.join(folder, entry_name)
            return os.path.relpath(path, start=config.ROOT_DIR)
    return None


def append_new_data(df: pd.DataFrame, i: int) -> set:
    id = df["order-item-id"][i]
    url = df["customized-url"][i]
    folder = os.path.join(config.DOWNLOADS_DIR, str(id))

    # Download zips
    if not os.path.isdir(folder):
        download_and_extract_zip(url, folder)

    json_file = find_first_child(folder, ".json")
    with open(json_file, 'r') as jf:
        json_data = json.load(jf)

    # Append data to DataFrame
    counters = set() # counting order properties
    row = df.index[i]
    
    # Set image path
    df.at[i, "image"] = find_first_child(folder, ".jpg")

    # Get web images
    customizations = json_data["customizationData"]["children"][0]["children"][0]["children"]
    for custom in customizations:
        option = str(custom.get("type"))
        if option == "OptionCustomization":
            selection = custom.get("optionSelection", {})
            label = str(custom.get("label"))
            for keyword in config.KEYWORDS:
                if keyword in label.lower():
                    label = keyword
                    break
            if type(selection) is dict:
                thumbnail = custom.get("optionSelection", {}).get("thumbnailImage")
                if thumbnail is not None:
                    df.at[row, label+" image"] = thumbnail.get("imageUrl")
        else:
            config.log(f"Unknown customization type: {option} for order-item-id: {id}")
    
    # Get data
    surfaces = json_data["version3.0"]["customizationInfo"]["surfaces"]
    for surface in surfaces:
        for area in surface.get("areas", []):
            option = str(area.get("customizationType"))
            label = str(area.get("label"))
            for keyword in config.KEYWORDS:
                if keyword in label.lower():
                    label = keyword
                    break
            if option == "Options":
                counters.add(label)
                value = str.lower(area.get("optionValue"))
                if config.MONTHS.get(value) is not None:
                    value = config.MONTHS[value]
                df.at[row, label] = value
            elif option == "TextPrinting":
                df.at[row, label+" text"] = area.get("text")
                df.at[row, "font"] = area.get("fontFamily")
            else:
                config.log(f"Unknown customization type: {option} for order-item-id: {id}")
    
    return counters


# Counts a column's orders and returns a formatted string
def countOrders(df: pd.DataFrame, column: str, simple: bool = False) -> str | None:
    if simple and column in df.columns:
        return f"{column} counts: {str(df[column].value_counts().index.size)}"

    if column not in df.columns or "quantity-purchased" not in df.columns:
        config.log(f"Cannot count orders for column: {column}")
        return None

    map = {}
    for index, value in df[column].items():
        if value == "" or pd.isna(value):
            continue
        quantity = df.loc[int(index), "quantity-purchased"]
        map[value] = map.get(value, 0) + int(quantity)
    map = dict(sorted(map.items()))
    map["Total"] = sum(map.values())

    output = f"<details><summary>{column} counts</summary><ul>"
    for key, value in map.items():
        output += f"<li>{key}: {value}</li>"
    output += "</ul></details>"

    return output


def main(tsv_path: str) -> tuple[pd.DataFrame, dict[str]] | None:
    if tsv_path is None or not os.path.exists(tsv_path):
        return None
    
    df = tsv_to_df(tsv_path)

    count = set()
    for i in range(len(df)):
        counters = append_new_data(df, i)
        if counters is not None:
            count = count.union(counters)
    
    output = dict()
    output["orders"] = countOrders(df, "order-id", simple=True)
    for column in count:
        output[column] = countOrders(df, column)
    
    return df, output

# for debugging
if __name__ == '__main__':
    main(config.TSV_PATH)