"""
Processing a Temperature data file from OpenWeatherMap and extract temperature.

Data Sample:
[{"city_id":3054643,
 "main":{"temp":264.8635,"temp_min":264.8635,"temp_max":264.8635,"pressure":1036,"humidity":93},
 "wind":{"speed":2,"deg":253},
 "rain":{"3h":0},
 "snow":{"3h":0},
 "clouds":{"all":78},
 "weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04"}],
 "dt":1420070400,
 "dt_iso":"2015-01-01 00:00:00 +0000 UTC"},

Result sample:
{"2015-01-01 00:00:00 +0000 UTC": 264.8635,
 "2015-01-01 01:00:00 +0000 UTC": 264.66834375,

Data Info:
    https://openweathermap.org/
    https://openweathermap.org/current
Code Samples:
    https://realpython.com/python-json/
    https://stackoverflow.com/questions/39450065/python-3-read-write-compressed-json-objects-from-to-gzip-file
"""
import json
import gzip

# DATA_FILE = "F:/tmp/ML/bud.json"
# DATA_FILE = "F:/tmp/ML/Budapest_OpenWeather.json"
DATA_FILEGZ = "F:/tmp/ML/Budapest_OpenWeather.json.gz"
OUT_FILE = "F:/tmp/ML/temp_bud.json.gz"

# read Data
with gzip.open(DATA_FILEGZ, "r") as read_file:
    data = json.load(read_file)

# temperature dictionary
temp_dict = dict()

# Iterate over
for weather_dict in data:
    timestamp = weather_dict['dt_iso']
    temperature = weather_dict["main"]["temp"]
    # print(f"Idő:{timestamp}, Hőmérséklet:{temperature}")
    temp_dict[timestamp] = temperature

# serialization
with gzip.open(OUT_FILE, "wt") as write_file:
    json.dump(temp_dict, write_file)
