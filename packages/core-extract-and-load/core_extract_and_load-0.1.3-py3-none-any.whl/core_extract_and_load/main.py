import requests
from dataclasses import dataclass
from typing import Any
import sqlite3

global GLOBAL_URL 
GLOBAL_URL = "https://api.bluelytics.com.ar/v2/latest"

@dataclass(frozen=True, slots=True)
class ValueDTO:
    value_avg: float
    value_sell: float
    value_buy: float

@dataclass(frozen=True, slots=True)
class ResponseDTO:
    oficial: ValueDTO
    blue: ValueDTO
    oficial_euro: ValueDTO
    blue_euro: ValueDTO
    last_update: str

def clean_data(data: Any) -> ResponseDTO:

    return ResponseDTO(
        oficial=ValueDTO(
            value_avg=data["oficial"]["value_avg"],
            value_sell=data["oficial"]["value_sell"],
            value_buy=data["oficial"]["value_buy"]
        ),
        blue=ValueDTO(
            value_avg=data["blue"]["value_avg"],
            value_sell=data["blue"]["value_sell"],
            value_buy=data["blue"]["value_buy"]
        ),
        oficial_euro=ValueDTO(
            value_avg=data["oficial_euro"]["value_avg"],
            value_sell=data["oficial_euro"]["value_sell"],
            value_buy=data["oficial_euro"]["value_buy"]
        ),
        blue_euro=ValueDTO(
            value_avg=data["blue_euro"]["value_avg"],
            value_sell=data["blue_euro"]["value_sell"],
            value_buy=data["blue_euro"]["value_buy"]
        ),
        last_update=data["last_update"]
    )    

def save_data(data: ResponseDTO, db_path:str):
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS cotizacion (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, value_avg REAL, value_sell REAL, value_buy REAL, last_update TEXT)")

    rows: list[tuple[str, float, float, float, str]] = [
        ("oficial", data.oficial.value_avg, data.oficial.value_sell, data.oficial.value_buy, data.last_update),
        ("blue", data.blue.value_avg, data.blue.value_sell, data.blue.value_buy, data.last_update),
        ("oficial_euro", data.oficial_euro.value_avg, data.oficial_euro.value_sell, data.oficial_euro.value_buy, data.last_update),
        ("blue_euro", data.blue_euro.value_avg, data.blue_euro.value_sell, data.blue_euro.value_buy, data.last_update)
    ]

    for row in rows:
        cursor.execute("INSERT INTO cotizacion (name, value_avg, value_sell, value_buy, last_update) VALUES (?, ?, ?, ?, ?)", row)

    conn.commit()
    conn.close()


def fetch_data(url: str) -> ResponseDTO:
    response = requests.get(url)

    if response.status_code == 200:
        raw_data = response.json()
        return clean_data(raw_data)
    else:
        raise Exception("Error al consultar la api")

def extract_and_load( db_path:str):

    data: ResponseDTO = fetch_data(GLOBAL_URL)

    save_data(data, db_path)

if __name__ == "__main__":
    import os
    DB_PATH = os.getenv('DB_PATH')
    extract_and_load(DB_PATH)


