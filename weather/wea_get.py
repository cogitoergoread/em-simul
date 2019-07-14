#!/home/users/muszi/python3-wrk/bin/python
"""
Aktuális időjárás adatok lekérdezése az OpenWeatherMap siteról.

Info:
    https://openweathermap.org/current
Script:
    https://stackoverflow.com/questions/48937900/round-time-to-nearest-hour-python
InfluxDB:
    https://github.com/influxdata/influxdb-python
URL város kódra:
    http://samples.openweathermap.org/data/2.5/weather?id=2172797&appid=b6907d289e10d714a6e88b30761fae22
Budapest kódja:
    {
    "id": {
      "$numberLong": "3054643"
    },
    "city": {
      "id": {
        "$numberLong": "3054643"
      },
      "name": "Budapest",
      "findname": "BUDAPEST",
      "country": "HU",
      "coord": {
        "lon": 19.039909,
        "lat": 47.498009
      },
      "zoom": {
        "$numberLong": "5"
      }
    }
  },
Eredmény:
    {
  "coord": {
    "lon": -122.08,
    "lat": 37.39
  },
  "weather": [
    {
      "id": 800,
      "main": "Clear",
      "description": "clear sky",
      "icon": "01d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 296.71,
    "pressure": 1013,
    "humidity": 53,
    "temp_min": 294.82,
    "temp_max": 298.71
  },
  "visibility": 16093,
  "wind": {
    "speed": 1.5,
    "deg": 350
  },
  "clouds": {
    "all": 1
  },
  "dt": 1560350645,
  "sys": {
    "type": 1,
    "id": 5122,
    "message": 0.0139,
    "country": "US",
    "sunrise": 1560343627,
    "sunset": 1560396563
  },
  "timezone": -25200,
  "id": 420006353,
  "name": "Mountain View",
  "cod": 200
}

"""
import requests
from datetime import datetime, timedelta
from influxdb import InfluxDBClient

OW_URL = "http://samples.openweathermap.org/data/2.5/weather?"
APP_ID = "6d5bd6e2352ffd5660f34f0d946fe91f"
BUD_ID = "3054643"
# INFL_HOST = "tick.rubin.hu"
INFL_HOST = "localhost"
INFL_PORT = 8086
INFL_USER = "telegraf"
INFL_PASS = "telegraf"
INFL_DB = "temperature"


def get_temp():
    response = requests.get(OW_URL + f"id={BUD_ID}&appid={APP_ID}")
    if response.status_code == 200:
        # returns the temperature
        json_dict = response.json()
        return json_dict['main']['temp']
    else:
        return "0.0"


def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
            + timedelta(hours=t.minute // 30))


def write_to_influx(timestamp: str, temperature: str):
    client = InfluxDBClient(INFL_HOST, INFL_PORT, INFL_USER, INFL_PASS, INFL_DB)
    infl_dict = [{"measurement": "temperature",
                  "time": timestamp,
                  "fields": {'temp': "{}".format(temperature)}}]
    retval = client.write_points(infl_dict)
    print("Ret:{}".format(retval))


if __name__ == '__main__':
    timestamp = datetime.now()
    rounded_timestamp = hour_rounder(timestamp)
    temperature = get_temp()
    print("Time:{}, Temperature:{}".format(rounded_timestamp, temperature))
    write_to_influx(rounded_timestamp, temperature)
