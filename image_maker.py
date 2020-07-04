# -*- coding: utf-8 -*-
import datetime
import os
import re

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from translitua import translit, RussianSimple

from data_base_updater import FORMAT_IN_DATE

TEMPLATE_PATH = 'files/postcard_base.jpg'
FONT_PATH = 'files/Roboto.ttf'

POSTCARD_PATH = 'postcards/'

FONT_SIZE = 30
FONT_COLOR = (0, 0, 0, 255)
FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE)

SUN_ICON = 'files/sun.png'
CLOUD_ICON = 'files/cloud.png'
SNOW_ICON = 'files/snow.png'
RAIN_ICON = 'files/rain.png'

TOWN_OFFSET = (50, 10)
DATE_OFFSET = (50, 50)
FORECAST_CONDITION_OFFSET = (50, 100)
DAY_TEMP_OFFSET = (50, 150)
NIGHT_TEMP_OFFSET = (50, 200)


class ImageMaker:
    def __init__(self, date, forecast_condition, temperature_day, temperature_night, town):
        self.date = datetime.date.strftime(date, FORMAT_IN_DATE)
        self.forecast_condition = forecast_condition
        self.temperature_day = temperature_day
        self.temperature_night = temperature_night
        self.town = town

    def generate_ticket(self):

        postcard_cv2 = self.paint_background()

        town_translit = translit(self.town, RussianSimple)
        postcard_name = f'postcard_{town_translit}_{self.date}.jpg'
        postcard_path = os.path.join(POSTCARD_PATH, postcard_name)
        os.makedirs(POSTCARD_PATH, exist_ok=True)
        cv2.imwrite(postcard_path, postcard_cv2)

        postcard_pillow = Image.open(postcard_path)

        draw = ImageDraw.Draw(postcard_pillow)
        draw.text(TOWN_OFFSET, self.town, font=FONT, fill=FONT_COLOR)
        draw.text(DATE_OFFSET, self.date, font=FONT, fill=FONT_COLOR)
        draw.text(FORECAST_CONDITION_OFFSET, self.forecast_condition, font=FONT, fill=FONT_COLOR)
        draw.text(DAY_TEMP_OFFSET, f'Температура днем: {self.temperature_day}°C', font=FONT, fill=FONT_COLOR)
        draw.text(NIGHT_TEMP_OFFSET, f'Температура ночью: {self.temperature_night}°C', font=FONT, fill=FONT_COLOR)

        postcard_pillow.save(postcard_path, 'JPEG')

    def paint_background(self):
        postcard_cv2 = cv2.imread(TEMPLATE_PATH)
        height, width = postcard_cv2.shape[:2]

        re_forecast_condition = self.forecast_condition.lower()
        re_sun = re.compile(r'ясно')
        re_cloud = re.compile(r'облач')
        re_rain = re.compile(r'дожд')
        re_snow = re.compile(r'сне')

        background_dict = {'sun': [re_sun, self.sun_background],
                           'cloud': [re_cloud, self.cloud_background],
                           'rain': [re_rain, self.rain_background],
                           'snow': [re_snow, self.snow_background]
                           }
        for background in background_dict.values():
            match = re.search(background[0], re_forecast_condition)
            if match:
                background[1](width, height, postcard_cv2)
                break

        return postcard_cv2

    def add_forecast_icon(self, img1, img2):
        bcols = img1.shape[1]
        rows, cols = img2.shape[:2]

        x_offset = bcols - cols
        y_offset = 0
        y1, y2 = y_offset, y_offset + rows
        x1, x2 = x_offset, x_offset + cols

        alpha_s = img2[:, :, 3] / 255
        alpha_l = 1 - alpha_s

        for c in range(3):
            img1[y1:y2, x1:x2, c] = (alpha_s * img2[:, :, c] + alpha_l * img1[y1:y2, x1:x2, c])

    def sun_background(self, width, height, postcard_cv2):
        # yellow
        for x in range(width + 1):
            contours = np.array([[x, 0], [x + 1, 0], [x + 1, height], [x, height]])
            cv2.fillPoly(postcard_cv2, pts=[contours], color=(int(255 * x / width), 255, 255))

        forecast_icon = cv2.imread(SUN_ICON, -1)
        self.add_forecast_icon(img1=postcard_cv2, img2=forecast_icon)

    def cloud_background(self, width, height, postcard_cv2):
        # grey
        for x in range(width + 1):
            grey_start = 700
            contours = np.array([[x, 0], [x + 1, 0], [x + 1, height], [x, height]])
            cv2.fillPoly(postcard_cv2, pts=[contours], color=(int(255 * (x + grey_start) / (width + grey_start)),
                                                              int(255 * (x + grey_start) / (width + grey_start)),
                                                              int(255 * (x + grey_start) / (width + grey_start))))

        forecast_icon = cv2.imread(CLOUD_ICON, -1)
        self.add_forecast_icon(img1=postcard_cv2, img2=forecast_icon)

    def rain_background(self, width, height, postcard_cv2):
        # dark_blue
        for x in range(width + 1):
            contours = np.array([[x, 0], [x + 1, 0], [x + 1, height], [x, height]])
            cv2.fillPoly(postcard_cv2, pts=[contours], color=(255, int(255 * x / width), int(255 * x / width)))

        forecast_icon = cv2.imread(RAIN_ICON, -1)
        self.add_forecast_icon(img1=postcard_cv2, img2=forecast_icon)

    def snow_background(self, width, height, postcard_cv2):
        # blue
        for x in range(width + 1):
            contours = np.array([[x, 0], [x + 1, 0], [x + 1, height], [x, height]])
            cv2.fillPoly(postcard_cv2, pts=[contours], color=(255, 255, int(255 * x / width)))

        forecast_icon = cv2.imread(SNOW_ICON, -1)
        self.add_forecast_icon(img1=postcard_cv2, img2=forecast_icon)


if __name__ == '__main__':
    img_maker = ImageMaker(date='30-06-2020', forecast_condition='дождь',
                           temperature_day='22', temperature_night='23', town='Коломна')
    img_maker.generate_ticket()
