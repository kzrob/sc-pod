import pandas as pd
import requests
import zipfile
import json
import os
from sqlalchemy import create_engine

tsv_data = "./input/1.txt"
download_folder = "./files/"

def install(url, local_filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for bad status codes

    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

df = pd.read_csv(tsv_data, sep="\t", encoding="utf-16") # Adjust encoding as needed
df = df.dropna(axis=1, how="all") # Drop columns that are completely empty

def append_new_data(i):
    id = df["order-item-id"][i]
    folder = download_folder + str(id)
    file = download_folder + str(id) + ".zip"

    install(df["customized-url"][i], file)
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(folder)

    json_file = folder + "/" + str(df["order-item-id"][i]) + ".json"
    with open(json_file, 'r') as json_file:
        data = json.load(json_file)

    # Use the actual DataFrame index for assignment to avoid KeyError and chained-assignment
    row_idx = df.index[i]

    # These `.at` assignments will create the columns if they don't exist and set the value for the row
    areas = data["version3.0"]["customizationInfo"]["surfaces"][0]["areas"]
    print(len(areas), end="")
    df.at[row_idx, "color"]          = areas[0]["optionValue"]
    df.at[row_idx, "engraving-side"] = areas[1]["optionValue"]
    df.at[row_idx, "logo-id"]        = areas[2]["optionValue"]
    df.at[row_idx, "font-style"]     = areas[3]["fontFamily"]
    df.at[row_idx, "side1"]          = areas[3]["text"]
    if len(areas) > 5:
        df.at[row_idx, "fast-shipping"]  = areas[5]["optionValue"]
        df.at[row_idx, "side2"] = areas[4]["text"]
    else:
        df.at[row_idx, "fast-shipping"]  = areas[4]["optionValue"]

    os.remove(file)
    
for i in range(len(df)):
    append_new_data(i)

print(df)

engine = create_engine('sqlite:///data.db')
df.to_sql(name='products', con=engine, if_exists='replace', index=False)
