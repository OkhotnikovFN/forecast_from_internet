# -*- coding: utf-8 -*-
import datetime
from pprint import pprint

import requests
import bs4

FORECAST_URL = 'https://yandex.ru/pogoda/'
FORMAT_OUT_DATE = '%Y-%m-%d %H:%M%z'


class WeatherMaker:
    def __init__(self):
        self.forecast_list = []

    def get_forecast(self):
        response = requests.get(FORECAST_URL)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        forecast_tags_list = soup.find_all(name='div', attrs={"class": "forecast-briefly__day"})
        town_name = soup.find_all(name="span", attrs={"class": "breadcrumbs__title", "itemprop": "name"})[-1].string

        self.forecast_list = []
        for daily_forecast_tag in forecast_tags_list:
            date_string = daily_forecast_tag.find(name='time').get('datetime')
            date = datetime.datetime.strptime(date_string, FORMAT_OUT_DATE).date()
            forecast_condition = daily_forecast_tag.find(attrs={"class": "forecast-briefly__condition"}).string
            temperature_day = daily_forecast_tag.find(attrs={'class': 'forecast-briefly__temp_day'}).find(
                attrs={'class': 'temp__value'}).string
            temperature_night = daily_forecast_tag.find(attrs={'class': 'forecast-briefly__temp_night'}).find(
                attrs={'class': 'temp__value'}).string
            daily_forecast = {"date": date,
                              "forecast_condition": forecast_condition,
                              "temperature_day": temperature_day,
                              "temperature_night": temperature_night,
                              "town": town_name.upper()}
            self.forecast_list.append(daily_forecast)

        self.forecast_list.sort(key=lambda x: x["date"])
        return self.forecast_list


if __name__ == '__main__':
    yandex_forecast = WeatherMaker()
    yandex_forecast.get_forecast()
    pprint(yandex_forecast.forecast_list)
