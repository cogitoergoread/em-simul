"""
OpenWeatherMap lapról adat olvasás.


Script:
    https://codereview.stackexchange.com/questions/204524/getting-current-weather-data-using-openweathermap-api
"""
from os.path import isfile
from io import StringIO
from datetime import datetime
from csv import DictWriter
import requests

URL = 'https://pm1aapplicantsdata.blob.core.windows.net/databases/CitiesWeather/CitiesWeather.csv'


class CityWeatherCollector(object):
    """Class to collect weather information for a given city from openweathermap.org
    """

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    apikey = 'xxxxxxxxxxxxxxxxxxxxxxx'

    def __init__(self, city, code):
        self.city = city
        self.code = code

    @property
    def full_url(self):
        return self.base_url + f"appid={self.apikey}&q={self.city},{self.code}"

    def fetch_data(self):
        response = requests.get(self.full_url)
        if response.status_code == 200:
            # returns a dictionary
            return response.json()
        else:
            raise WeatherCollectionError(f"Response from API was: {response.status_code}")


class WeatherCollectionError(Exception):
    pass


class WeatherDataWriter(object):

    def __init__(self, full_filepath):
        self.full_filepath = full_filepath


class WeatherData(object):
    """Class for a representation of the data"""

    def __init__(self, name, country, temp, humidity, pressure, visibility, wind_speed, timestamp=datetime.now()):
        self.name = name
        self.country = country
        self.temp = temp
        self.humidity = humidity
        self.pressure = pressure
        self.visibility = visibility
        self.wind_speed = wind_speed
        self.timestamp = timestamp

    @staticmethod
    def create_from_json(json_dict, timestamp=datetime.now()):
        return WeatherData(
            name=json_dict['name'],
            country=json_dict['sys']['country'],
            temp=json_dict['main']['temp'],
            humidity=json_dict['main']['humidity'],
            pressure=json_dict['main']['pressure'],
            visibility=json_dict['visibility'],
            wind_speed=json_dict['wind']['speed'],
            timestamp=timestamp
        )

    def write_one(self, outfile):
        weather_data = self.__dict__
        # if file exists, append
        csv_writer = DictWriter(
            out_file,
            fieldnames=list(weather_data.keys()),
            delimiter=',',
            lineterminator='\n'
        )
        # if the file is empty write header
        if outfile.tell() == 0:
            csv_writer.writeheader()
        csv_writer.writerow(weather_data)


def get_cities(url=URL):
    response = requests.get(url)
    if response.status_code == 200:
        decoded_response = StringIO(response.content.decode('utf8'))
        # pop the headings
        next(decoded_response)
        for line in decoded_response:
            city, code = tuple(line.strip().split(','))
            yield CityWeatherCollector(city, code)


if __name__ == '__main__':
    timestamp = datetime.now()
    with open('data.csv', 'a') as out_file:
        for collector in get_cities(URL):
            # add error handling
            full_data = collector.fetch_data()
            data = WeatherData.create_from_json(json_dict=full_data, timestamp=timestamp)
            data.write_one(out_file)
