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


def download_and_extract_zip(url: str, folder: str) -> None:
    # Download zip
    zip = folder + ".zip"
    response = requests.get(url, stream=True)
    response.raise_for_status()

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
        match option:
            case "OptionCustomization":
                selection = custom.get("optionSelection", {})
                label = str(custom.get("label")).lower()
                for keyword in config.KEYWORDS:
                    label = keyword if keyword in label else label
                if type(selection) is dict:
                    thumbnail = custom.get("optionSelection", {}).get("thumbnailImage")
                    if thumbnail is not None:
                        df.at[row, label+" image"] = thumbnail.get("imageUrl")
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
            match option:
                case "Options":
                    counters.add(label)
                    value = str.lower(area.get("optionValue"))
                    if config.MONTHS.get(value) is not None:
                        value = config.MONTHS[value]
                    df.at[row, label] = value
                case "TextPrinting":
                    df.at[row, label+" text"] = area.get("text")
                    df.at[row, "font"] = area.get("fontFamily")
                case _:
                    config.log(f"Unknown customization type: {option} for order-item-id: {id}")
    
    return counters


def append_image_data(df: pd.DataFrame, i: int) -> list[str]:
    id = df["order-item-id"][i]
    url = df["customized-url"][i]
    folder = os.path.join(config.DOWNLOADS_DIR, str(id))

    # Download zips
    if not os.path.isdir(folder):
        download_and_extract_zip(url, folder)

    json_file = find_first_child(folder, ".json")
    with open(json_file, 'r') as jf:
        json_data = json.load(jf)

    # Set image path
    image_name = json_data["customizationData"]["children"][0]["children"][0]["children"][0]["children"][0]["image"]["imageName"]
    path = os.path.relpath(os.path.join(folder, image_name), start=config.ROOT_DIR)

    Shapes = {
        "B0CJMBCZMH": "A-heart",
        "B0FLJG1N3Q": "A-heart",
        "B0CJM73FBW": "A-oval",
        "B0FLHZ9NT5": "A-oval",
        "B0FLJ3BS1Z": "A-oval",
        "B09XTV129V": "A-oval",
        "B0CJM7BLGB": "A-rectangle",
        "B0FLHXDJRY": "A-rectangle",
        "B0CJLRD61X": "B-doubleheart",
        "B0FLJMFR8N": "B-doubleheart",
        "B0CJM7KLX9": "B-doubleround",
        "B0CJM7371N": "C-fourpicture",
        "B0FLD4SGSL": "D-leather",
    }

    print(json_data["asin"])
    return {
        "id": df["order-id"][i],
        "image1": path,
        "image2": None,
        "shape": Shapes[json_data["asin"]],
        "quantity": json_data["quantity"],
    }

# Counts a column's orders and returns a formatted string
def count_orders(df: pd.DataFrame, column: str, simple: bool = False) -> str | None:
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
    for i in range(len(df)):
        counters = append_new_data(df, i)
        if counters is not None:
            count = count.union(counters)
    
    output = dict()
    output["orders"] = count_orders(df, "order-id", simple=True)
    for column in count:
        output[column] = count_orders(df, column)
    
    return df, output


def process_gallery(tsv_path: str) -> list[list[str]] | None:
    if tsv_path is None or not os.path.exists(tsv_path):
        return None
    
    df = tsv_to_df(tsv_path)
    if df is None:
        return None
    output = []
    for i in range(len(df)):
        output.append(append_image_data(df, i))

    return output
