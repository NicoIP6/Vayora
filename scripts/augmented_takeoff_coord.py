import requests
import os
import json
from time import sleep


def reverse_geocode(lat: float, lon: float):
    url = f"https://geocode.maps.co/reverse?lat={lat}&lon={lon}&api_key={api_key}"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    # Extraction simple
    address = data.get("address", {})

    return {
        "city": address.get("city") or address.get("town") or address.get("village"),
        "country": address.get("country"),
        "country_code": address.get("country_code"),
        "street": address.get("road"),
        "postal_code": address.get("postcode"),
    }


if __name__ == "__main__":

    api_key = os.environ.get('GEOCODE_API_KEY')

    with open("/home/nico/Documents/TECHNOBEL_Data_Analyse/Flask_ORM/formated_takeoff_geoCor.json", "r") as f:
        data = json.load(f)

    augmented_takeoff_coord = []
    for dic in data:

        lat = dic["Latitude"]
        lon = dic["Longitude"]

        result = reverse_geocode(lat, lon)
        augmented_takeoff_coord.append({**dic, **result})
        print(result)
        sleep(5)

    json.dump(augmented_takeoff_coord, open("../data/takeoff_data/takeoff_full.json", "w"), ensure_ascii=False, indent=4)

