import peewee
import datetime
from playhouse.db_url import connect

from init_forecast_database import DATABASE_PATH
from weather_maker import WeatherMaker

FORMAT_IN_DATE = '%Y-%m-%d'


class DataBaseUpdater:

    def __init__(self, database_path):
        self.database = connect(f'sqlite:///{database_path}')

        class Forecast(peewee.Model):
            date = peewee.DateField()
            forecast_condition = peewee.CharField()
            temperature_day = peewee.CharField()
            temperature_night = peewee.CharField()
            town = peewee.CharField()

            class Meta:
                database = self.database

        self.Forecast = Forecast
        self.Forecast.create_table()

    def get_forecast_from_db(self, start_date, end_date, town=None):
        start_date, end_date = self._format_str_to_date(start_date, end_date)

        forecast_list = []
        for forecast in self._get_forecast_list(start_date, end_date, town):
            forecast_list.append({
                "date": forecast.date,
                "forecast_condition": forecast.forecast_condition,
                "temperature_day": forecast.temperature_day,
                "temperature_night": forecast.temperature_night,
                "town": forecast.town
            })

        return forecast_list

    def _get_forecast_list(self, start_date, end_date, town):
        if town:
            return self.Forecast.select().where((self.Forecast.date >= start_date) &
                                                (self.Forecast.date <= end_date) &
                                                (self.Forecast.town == town)).order_by(self.Forecast.date)
        else:
            return self.Forecast.select().where((self.Forecast.date >= start_date) &
                                                (self.Forecast.date <= end_date)).order_by(self.Forecast.date)

    def write_forecast_to_db(self, start_date, end_date):
        start_date, end_date = self._format_str_to_date(start_date, end_date)

        weather_getter = WeatherMaker()
        possible_forecast_list = weather_getter.get_forecast()
        town = possible_forecast_list[0]["town"]

        existing_forecasts = []
        for forecast in self._get_forecast_list(start_date, end_date, town):
            existing_forecasts.append({"date": forecast.date, "town": forecast.town})

        forecast_add_to_base = []
        for forecast in possible_forecast_list:
            possible_forecast = {"date": forecast["date"], "town": town}
            if start_date <= forecast["date"] <= end_date and possible_forecast not in existing_forecasts:
                forecast_add_to_base.append(forecast)

        for forecast in possible_forecast_list:
            (self.Forecast.update(**forecast)
             .where((self.Forecast.town == forecast["town"]) & (self.Forecast.date == forecast["date"]))
             .execute())

        self.Forecast.insert_many(forecast_add_to_base).execute()
        return forecast_add_to_base, existing_forecasts

    def _format_str_to_date(self, start_date, end_date):
        start_date = datetime.datetime.strptime(start_date, FORMAT_IN_DATE).date()
        end_date = datetime.datetime.strptime(end_date, FORMAT_IN_DATE).date()
        return start_date, end_date


if __name__ == '__main__':
    db_update = DataBaseUpdater(DATABASE_PATH)
    db_update.write_forecast_to_db(start_date='2020-6-4', end_date='2020-7-10')
# -get 2020-6-4 2020-7-10
