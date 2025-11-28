import definitions as defs
import pandas as pd

def keychain_handler(df: pd.DataFrame, json_data, i: int, store: str) -> None:
    areas = json_data["version3.0"]["customizationInfo"]["surfaces"][0]["areas"]
    logo_id = areas[2]["optionValue"]
    if logo_id.isdigit():
        df.at[i, "logo-image"] = f"/files/{store}_keychain/{logo_id.lstrip('0')}.png"
    elif logo_id[1:].isdigit():
        df.at[i, "logo-image"] = f"/files/{store}_keychain/{logo_id[1:].lstrip('0')}.png"
    df.at[i, "image"] = "/files/" + str(df.iloc[i]["order-item-id"]) + "/.jpg"
    df.at[i, "color"] = areas[0]["optionValue"]
    df.at[i, "engraving-side"] = areas[1]["optionValue"]
    df.at[i, "font"] = areas[3]["fontFamily"]
    df.at[i, "front-side"] = areas[3]["text"]
    if len(areas) > 5:
        df.at[i, "fast-shipping"] = areas[5]["optionValue"]
        df.at[i, "back-side"] = areas[4]["text"]
    else:
        df.at[i, "fast-shipping"] = areas[4]["optionValue"]

def jubope_keychain(df: pd.DataFrame, json_data, i: int) -> None:
    keychain_handler(df, json_data, i, "jubope")

def cdbuy_keychain(df: pd.DataFrame, json_data, i: int) -> None:
    keychain_handler(df, json_data, i, "cdbuy")

def jubope_bracelet(df: pd.DataFrame, json_data, i: int) -> None:
    areas = json_data["version3.0"]["customizationInfo"]["surfaces"][0]["areas"]
    df.at[i, "image"] = "/files/" + str(df.iloc[i]["order-item-id"]) + "/.jpg"
    df.at[i, "color"] = areas[0]["optionValue"]
    birthstone = defs.MONTHS_3.get(areas[1]["optionValue"])
    if birthstone is None:
        birthstone = ""
    else:
        df.at[i, "birthstone-image"] = json_data["customizationData"]["children"][0]["children"][0]["children"][1]["optionSelection"]["thumbnailImage"]["imageUrl"]
    df.at[i, "birthstone-id"] = str(birthstone)
    thumbnail = json_data["customizationData"]["children"][0]["children"][0]["children"][2]["optionSelection"].get("thumbnailImage")
    if thumbnail is not None:
        df.at[i, "logo-image"] = thumbnail["imageUrl"]
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