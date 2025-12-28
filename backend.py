import config
import pandas as pd
import requests
import zipfile
import json
import os
import chardet

def tsv_to_df(tsv: str, sample_size: int = 10000) -> pd.DataFrame | None:
    if os.path.getsize(tsv) <= 0:
        return None

    # Detect encoding
    with open(tsv, 'rb') as f:
        rawdata = f.read(sample_size)
    encoding = chardet.detect(rawdata)["encoding"]

    # Read TSV into DataFrame
    df = pd.read_csv(tsv, sep="\t", encoding=encoding) 
    df = df.dropna(axis=1, how="all")  # Drop columns that are completely empty
    return df


def download_and_extract_zip(url: str, folder: str) -> bool:
    # Download zip
    zip = folder + ".zip"
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
    except requests.HTTPError as e:
        config.log(f"Failed to download zip from {url}: {e}")
        return False

    # Write zip to disk
    with open(zip, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Extract zip into folder and remove when done
    with zipfile.ZipFile(zip, 'r') as zip_ref:
        zip_ref.extractall(folder)
    os.remove(zip)

    return True


def find_first_child(folder, extension: str) -> str | None:
    for entry_name in os.listdir(folder):
        if extension in entry_name:
            path = os.path.join(folder, entry_name)
            return os.path.relpath(path, start=config.ROOT_DIR)
    return None


def download_json_data(url: str, folder):
    if not os.path.isdir(folder):
        success = download_and_extract_zip(url, folder)
        if success == False:
            return None

    json_file = find_first_child(folder, ".json")
    with open(json_file, 'r') as jf:
        return json.load(jf)


def append_table_data(df: pd.DataFrame, i: int) -> set | None:
    id = df["order-item-id"][i]
    url = df["customized-url"][i]
    folder = os.path.join(config.DOWNLOADS_DIR, str(id))
    json_data = download_json_data(url, folder)
    output = set() # counting order properties

    if json_data is None:
        return None

    # Get image
    df.at[i, "image"] = find_first_child(folder, ".jpg")
    
    # Get web images
    customizations = json_data["customizationData"]["children"][0]["children"][0]["children"]
    for custom in customizations:
        option = str(custom.get("type"))
        match option:
            case "OptionCustomization":
                selection = custom.get("optionSelection", {})
                label = str(custom.get("label")).lower()
                for keyword in config.KEYWORDS:
                    label = keyword if keyword in label else label
                if type(selection) is dict:
                    thumbnail = custom.get("optionSelection", {}).get("thumbnailImage")
                    if thumbnail is not None:
                        df.at[i, label+" image"] = thumbnail.get("imageUrl")
            case _:
                config.log(f"Unknown customization type: {option} for order-item-id: {id}")
    
    # Get data
    surfaces = json_data["version3.0"]["customizationInfo"]["surfaces"]
    for surface in surfaces:
        for area in surface.get("areas", []):
            option = str(area.get("customizationType"))
            label = str(area.get("label")).lower()
            for keyword in config.KEYWORDS:
                label = keyword if keyword in label else label
            if label == "more":
                value = str(area.get("optionValue"))
                value = ''.join(char for char in value if char.isdigit())
                df.at[i, "quantity-purchased"] = int(df.at[i, "quantity-purchased"]) * int(value)
                continue
            match option:
                case "Options":
                    output.add(label)
                    value = str.lower(area.get("optionValue"))
                    value = config.MONTHS.get(value, value)
                    df.at[i, label] = value
                case "TextPrinting":
                    df.at[i, label+" text"] = area.get("text")
                    df.at[i, "font"] = area.get("fontFamily")
                case _:
                    config.log(f"Unknown customization type: {option} for order-item-id: {id}")
    
    return output


def append_gallery_data(df: pd.DataFrame, i: int) -> list[str] | None:
    id = df["order-item-id"][i]
    url = df["customized-url"][i]
    folder = os.path.join(config.DOWNLOADS_DIR, str(id))
    json_data = download_json_data(url, folder)

    if json_data is None:
        return None
    
    # Set image path
    image1 = json_data["customizationData"]["children"][0]["children"][0]["children"][0]["children"][0]["image"]["imageName"]
    path1 = os.path.relpath(os.path.join(folder, image1), start=config.ROOT_DIR)
    try:
        image2 = json_data["customizationData"]["children"][0]["children"][0]["children"][1]["children"][0]["image"]["imageName"]
        path2 = os.path.relpath(os.path.join(folder, image2), start=config.ROOT_DIR)
    except (IndexError, KeyError):
        image2 = None
        path2 = None

    return {
        "id": df["order-id"][i],
        "image1": path1,
        "image2": path2,
        "shape": config.GALLERY_SHAPES[json_data["asin"]],
        "quantity": df["quantity-purchased"][i],
    }


# Counts a column's orders and returns a formatted string
def count_table_orders(df: pd.DataFrame, column: str, simple: bool = False) -> str | None:
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


def process_table(tsv_path: str) -> tuple[pd.DataFrame, dict[str]] | tuple[None, None]:
    if tsv_path is None or not os.path.exists(tsv_path):
        return None, None
    
    df = tsv_to_df(tsv_path)

    count = set()
    fails = 0
    for i in range(len(df)):
        counters = append_table_data(df, i)
        if counters is None:
            fails += 1
        else:
            count = count.union(counters)
    
    output = dict()
    output["orders"] = count_table_orders(df, "order-id", simple=True)
    output["failed-downloads"] = f"Failed downloads: {fails}"
    for column in count:
        output[column] = count_table_orders(df, column)
    
    return df, output


def process_gallery(tsv_path: str) -> list[list[str]] | None:
    if tsv_path is None or not os.path.exists(tsv_path):
        return None
    
    df = tsv_to_df(tsv_path)
    if df is None:
        return None
    output = []
    for i in range(len(df)):
        append_table_data(df, i)
        gallery_result = append_gallery_data(df, i)
        if gallery_result is not None:
            output.append(gallery_result)

    return output
