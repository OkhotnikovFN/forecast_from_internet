# -*- coding: utf-8 -*-
import datetime

from data_base_updater import DataBaseUpdater, FORMAT_IN_DATE
from image_maker import ImageMaker
from init_forecast_database import DATABASE_PATH
from weather_maker import WeatherMaker

INIT_EXIT = '-exit'
INIT_HELP = '-help'
INIT_GET = '-get'
INIT_LOAD = '-load'
INIT_FORECAST = '-forecast'
INIT_IMAGE = '-image'

HELP_TEXT = (f'Программа позволяет загружать краткий прогноз погоды из яндекс погоды\n'
             f'Доступные дейтсвия:\n'
             f'{INIT_EXIT} - выход из программы'
             f'{INIT_HELP} - вызов справки\n'
             f'{INIT_GET} (дата_1) (дата_2) (город) - получить прогноз погоды из базы данных  '
             f'(с дата_1 по дата_2)(формат даты: год-месяц-число)\n'
             f'{INIT_LOAD} - загрузить прогнозы в базу данных\n'
             f'{INIT_FORECAST} - просмотреть полученные прогнозы из базы данных\n'
             f'{INIT_IMAGE} - создание открыток из полученных прогнозов из базы данных')


class UserInterface:

    def __init__(self):
        self.db_updater = DataBaseUpdater(DATABASE_PATH)
        self.loaded_forecast = []

    def greeting(self):
        print(HELP_TEXT)

        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=6)

        start_date = datetime.date.strftime(start_date, FORMAT_IN_DATE)
        end_date = datetime.date.strftime(end_date, FORMAT_IN_DATE)
        self.loaded_forecast = self.db_updater.get_forecast_from_db(start_date, end_date)

        if self.loaded_forecast:
            print(f'Загружен прогноз c {self.loaded_forecast[0]["date"]} по {end_date}')
        else:
            print("В базе нету прогнозов за предшествующий период")

    def go(self):

        self.greeting()

        while True:
            user_text = input()
            if user_text == INIT_EXIT:
                break

            if user_text == INIT_HELP:
                print(HELP_TEXT)
                continue

            if user_text == INIT_FORECAST:
                self._view_forecast()
                continue

            if user_text.startswith(INIT_GET):
                self._get_from_db(user_text)
                continue

            if user_text.startswith(INIT_LOAD):
                self._load_to_db(user_text)
                continue

            if user_text == INIT_IMAGE:
                self._make_image()
                continue

    def _make_image(self):
        if self.loaded_forecast:
            for forecast in self.loaded_forecast:
                image_maker = ImageMaker(**forecast)
                image_maker.generate_ticket()
            print(f'Созданы открытки по прогнозам загруженным из базы данных')
        else:
            print("Сначала загрузите прогнозы из базы")

    def _get_from_db(self, user_text):
        dates = user_text.split(' ')

        if len(dates) not in [3, 4]:
            print('Неправильный формат запроса данных из базы данных, для подсказки введите -help')
            return
        start_date = dates[1]
        end_date = dates[2]
        town = None

        if len(dates) == 4:
            town = dates[3].upper()

        try:
            date_1 = datetime.datetime.strptime(start_date, FORMAT_IN_DATE).date()
            date_2 = datetime.datetime.strptime(end_date, FORMAT_IN_DATE).date()
        except ValueError:
            print('Неправильно введены даты, для подсказки введите -help')
            return

        if date_1 > date_2:
            print('Конечная дата не может быть раньше начальной повторите ввод')
            return

        temp_forecast = self.db_updater.get_forecast_from_db(start_date=start_date, end_date=end_date, town=town)
        if temp_forecast:
            self.loaded_forecast = temp_forecast
            print(f'Загружен прогноз c {self.loaded_forecast[0]["date"]} по {end_date}')
        else:
            print(f'Для указанных параметров поиска в базе данных нету записей')

    def _load_to_db(self, user_text):
        dates = user_text.split(' ')
        if len(dates) != 3:
            print('Неправильный формат запроса для записи данных в базу, для подсказки введите -help')
            return
        start_date = dates[1]
        end_date = dates[2]
        try:
            date_1 = datetime.datetime.strptime(start_date, FORMAT_IN_DATE).date()
            date_2 = datetime.datetime.strptime(end_date, FORMAT_IN_DATE).date()
        except ValueError:
            print('Неправильно введены даты, для подсказки введите -help')
            return
        if date_1 > date_2:
            print('Конечная дата не может быть раньше начальной повторите ввод')
            return
        weather_getter = WeatherMaker()
        possible_forecast_list = weather_getter.get_forecast()

        forecast_add_to_base, existing_forecasts = self.db_updater.write_forecast_to_db(start_date=start_date,
                                                                                        end_date=end_date)
        if forecast_add_to_base:
            print(f'В базу добавлены прогнозы по городу {forecast_add_to_base[0]["town"]} '
                  f'за диапазон дат ({forecast_add_to_base[0]["date"]} - {forecast_add_to_base[-1]["date"]})')
        if existing_forecasts:
            print(f'В базе обновлены прогнозы по городу {existing_forecasts[0]["town"]} '
                  f'за диапазон дат ({existing_forecasts[0]["date"]} - {existing_forecasts[-1]["date"]})\n')
        print(f'Сейчас из яндекс погоды возможно получить прогнозы с '
              f'{possible_forecast_list[0]["date"]} по {possible_forecast_list[-1]["date"]}')

    def _view_forecast(self):
        if self.loaded_forecast:
            for forecast in self.loaded_forecast:
                print(f'Город: {forecast["town"]} '
                      f'Дата: {forecast["date"]} '
                      f'Погодное состояние: {forecast["forecast_condition"]} '
                      f'Температура днем: {forecast["temperature_day"]} '
                      f'Температура ночью: {forecast["temperature_night"]}\n')
        else:
            print("Сначала загрузите прогнозы из базы")


user_interface = UserInterface()
user_interface.go()
