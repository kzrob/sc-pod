import pandas as pd

def jubope_keychain(df: pd.DataFrame, json_data, i: int) -> None:
    areas = json_data["version3.0"]["customizationInfo"]["surfaces"][0]["areas"]
    logo_id = areas[2]["optionValue"]
    if logo_id.isdigit():
        df.at[i, "logo"] = "/files/jubope_keychain/" + logo_id + ".png"
    elif logo_id[1:].isdigit():
        df.at[i, "logo"] = "/files/jubope_keychain/" + logo_id[1:] + ".png"
    else:
        df.at[i, "logo"] = "None"
    df.at[i, "image"] = "/files/" + str(df.iloc[i]["order-item-id"]) + "/.jpg"
    df.at[i, "color"] = areas[0]["optionValue"]
    df.at[i, "engraving-side"] = areas[1]["optionValue"]
    df.at[i, "font"] = areas[3]["fontFamily"]
    df.at[i, "side1"] = areas[3]["text"]
    if len(areas) > 5:
        df.at[i, "fast-shipping"] = areas[5]["optionValue"]
        df.at[i, "side2"] = areas[4]["text"]
    else:
        df.at[i, "fast-shipping"] = areas[4]["optionValue"]

def cdbuy_keychain():
    pass

def jubope_bracelet(df: pd.DataFrame, json_data, i: int) -> None:
    areas = json_data["version3.0"]["customizationInfo"]["surfaces"][0]["areas"]
    df.at[i, "image"] = "/files/" + str(df.iloc[i]["order-item-id"]) + "/.jpg"
    df.at[i, "color"] = areas[0]["optionValue"]
    df.at[i, "birthstone"] = areas[1]["optionValue"]
    thumbnail = json_data["customizationData"]["children"][0]["children"][0]["children"][2]["optionSelection"].get("thumbnailImage")
    if thumbnail is None:
        df.at[i, "logo"] = "None"
    else:
        df.at[i, "logo"] = thumbnail["imageUrl"]
    df.at[i, "font"] = areas[3]["fontFamily"]
    df.at[i, "front-side"] = areas[3]["text"]
    if len(areas) > 5:
        df.at[i, "fast-shipping"] = areas[5]["optionValue"]
        df.at[i, "back-side"] = areas[4]["text"]
    else:
        df.at[i, "fast-shipping"] = areas[4]["optionValue"]

# URLs: https://www.amazon.com/dp/{ASIN}
STORE_ASIN_MAP = {
    "B0D3GH5QX4": jubope_keychain,
    "B0FJ8PKYHM": jubope_keychain,
    "B0FHKXX9S7": cdbuy_keychain,
    "B0C7L8D3RH": jubope_bracelet,
}

def process(asin: str, df: pd.DataFrame, json_data, i: int) -> bool:
    handler = STORE_ASIN_MAP.get(asin)
    if handler is None:
        return False
    handler(df, json_data, i)
    return True