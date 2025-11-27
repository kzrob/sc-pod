# Product: https://www.amazon.com/dp/B0D3GH5QX4
def jubope_keychain(df, json_data, i):
    areas = json_data["version3.0"]["customizationInfo"]["surfaces"][0]["areas"]
    logo_id = areas[2].get("optionValue")
    if logo_id.isdigit():
        df.at[i, "logo"] = "/files/jubope_keychain/" + logo_id + ".png"
    elif logo_id[1:].isdigit():
        df.at[i, "logo"] = "/files/jubope_keychain/" + logo_id[1:] + ".png"
    else:
        df.at[i, "logo"] = "None"
    df.at[i, "image"] = "/files/" + str(df.iloc[i]["order-item-id"]) + "/.jpg"
    df.at[i, "color"] = areas[0].get("optionValue")
    df.at[i, "engraving-side"] = areas[1].get("optionValue")
    df.at[i, "font"] = areas[3].get("fontFamily")
    df.at[i, "side1"] = areas[3].get("text")
    if len(areas) > 5:
        df.at[i, "fast-shipping"] = areas[5].get("optionValue")
        df.at[i, "side2"] = areas[4].get("text")
    else:
        df.at[i, "fast-shipping"] = areas[4].get("optionValue")

# Product: https://www.amazon.com/dp/B0FHKXX9S7
def cdbuy_keychain():
    pass

# Product: https://www.amazon.com/dp/B0C7L8D3RH
def jubope_bracelet(df, json_data, i):
    areas = json_data["version3.0"]["customizationInfo"]["surfaces"][0]["areas"]
    df.at[i, "image"] = "/files/" + str(df.iloc[i]["order-item-id"]) + "/.jpg"
    df.at[i, "color"] = areas[0].get("optionValue")
    df.at[i, "birthstone"] = areas[1].get("optionValue")
    df.at[i, "logo"] = json_data["customizationData"]["children"][0]["children"][0]["children"][2]["optionSelection"].get("thumbnailImage")["imageUrl"]
    df.at[i, "font"] = areas[3].get("fontFamily")
    df.at[i, "front-side"] = areas[3].get("text")
    if len(areas) > 5:
        df.at[i, "fast-shipping"] = areas[5].get("optionValue")
        df.at[i, "back-side"] = areas[4].get("text")
    else:
        df.at[i, "fast-shipping"] = areas[4].get("optionValue")