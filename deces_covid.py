import urllib.request
from urllib.error import URLError, HTTPError
import json
import random
from PIL import Image, ImageDraw, ImageFont
import time
from sys import exit

start_time = time.time()
font_regular = ImageFont.truetype("arial.ttf", size=10)
font_small = ImageFont.truetype("arial.ttf", size=8)


def calc_moving_average(data, n):
    past_n_days = data[-n:]
    sum_values = 0
    for day in past_n_days:
        sum_values += day["daily_deaths"]
    n_moving_average = int(sum_values / n)
    return n_moving_average


def print_ten_thousand_text(draw, total_deaths, date, line_y, text_left):
    line_y -= 2
    ten_thousand_text_date = date
    ten_thousand_text_deaths = str(total_deaths)
    ten_thousand_text_date_width, ten_thousand_text_date_height = draw.textsize(ten_thousand_text_date, font=font_small)
    ten_thousand_text_deaths_width, ten_thousand_text_deaths_height = draw.textsize(ten_thousand_text_deaths, font=font_regular)
    draw.text((text_left, line_y - ten_thousand_text_deaths_height - ten_thousand_text_date_height),
              ten_thousand_text_date,
              font=font_small,
              fill=(255, 0, 0))
    draw.text((text_left, line_y - ten_thousand_text_deaths_height),
              ten_thousand_text_deaths + " morts",
              font=font_regular,
              fill=(255, 0, 0))


def print_new_year(draw, year, line_y, year_left):
    line_y -= 1
    new_year = year + 1
    year_width, year_height = draw.textsize(str(year), font=font_regular)
    draw.text((year_left, line_y - year_height),
              str(year),
              font=font_regular,
              fill=(0, 0, 255))
    draw.text((year_left, line_y),
              str(new_year),
              font=font_regular,
              fill=(0, 0, 255))


def generate_image(data):
    nb_days = len(data)
    margin = 15
    max_moving_average = max(item['moving_average'] for item in data)
    margin_top = 50
    margin_bottom = 30
    margin_right = 6 * margin
    line_multiplier = 2
    day_line_length = 3
    day_line_margin = 2

    ten_thousand_deaths_length = 3 * margin
    img_height = line_multiplier * nb_days + margin_top + margin_bottom + 2 * margin
    img_width = int(max_moving_average / line_multiplier) + 2 * margin + margin_right
    text_left = img_width - margin_right
    img = Image.new(mode="RGB", size=(img_width, img_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    title = "MORTS DU COVID-19 EN FRANCE DU " + data[0]['date'] + " AU " + data[-1]['date']
    title_width, title_height = draw.textsize(title, font=font_regular)

    sub_title_1 = "1 pixel noir = 1 décès"
    sub_title_1_width, sub_title_1_height = draw.textsize(sub_title_1, font=font_regular)
    sub_title_2 = "Décès lissés sur 7 jours"

    footer_1 = "David Bertho"
    footer_2 = "bertho.eu/covid"
    source_1 = "Source : Ministère des Solidarités et de la Santé"
    source_2 = "data.gouv.fr"

    footer_1_width, footer_1_height = draw.textsize(footer_1, font=font_regular)
    footer_2_width, footer_2_height = draw.textsize(footer_2, font=font_regular)
    source_1_width, source_1_height = draw.textsize(source_1, font=font_regular)
    source_2_width, source_2_height = draw.textsize(source_2, font=font_regular)
    footer_width = max(footer_1_width, footer_2_width)

    draw.text(((img_width-title_width)/2, 10),
              title,
              font=font_regular,
              fill=(0, 0, 0))

    draw.text((margin, 10 + title_height * 2),
              sub_title_1,
              font=font_regular,
              fill=(0, 0, 0))
    draw.text((margin,
               10 + title_height * 2 + sub_title_1_height),
              sub_title_2,
              font=font_regular,
              fill=(0, 0, 0))

    draw.text((margin,
               img_height - margin_bottom - source_2_height),
              source_1,
              font=font_regular,
              fill=(0, 0, 0))
    draw.text((margin,
               img_height - margin_bottom),
              source_2,
              font=font_regular,
              fill=(0, 0, 0))

    draw.text((img_width - margin - footer_1_width,
               img_height - margin_bottom - footer_2_height),
              footer_1,
              font=font_regular,
              fill=(0, 0, 0))
    draw.text((img_width - margin - footer_2_width,
               img_height - margin_bottom),
              footer_2,
              font=font_regular,
              fill=(0, 0, 0))

    day_increment = 0
    ten_thousand_deaths = 0
    year = int(data[0]['date'][0:4])

    for day in data:

        single_victim = 0
        line_y = margin + margin_top + day_increment * line_multiplier

        while single_victim < day["moving_average"]:
            pixel_x = random.randint(margin,
                                     img_width - margin - margin_right - 1)
            pixel_y = random.randint(margin_top + margin + day_increment * line_multiplier,
                                     margin_top + margin + (day_increment + 1) * line_multiplier)
            if img.getpixel((pixel_x, pixel_y)) == (255, 255, 255):
                img.putpixel((pixel_x, pixel_y), (0, 0, 0))
                single_victim += 1

        if int(day["total_deaths"] / 10000) > ten_thousand_deaths:
            ten_thousand_deaths = int(day["total_deaths"] / 10000)
            draw.line((margin - day_line_margin,
                       line_y,
                       img_width - margin - margin_right + ten_thousand_deaths_length,
                       line_y),
                      fill=(255, 0, 0),
                      width=1)
            print_ten_thousand_text(draw, day["total_deaths"], day["date"], line_y, text_left)
        else:
            draw.line((img_width - margin - margin_right + day_line_margin,
                       line_y,
                       img_width - margin - margin_right + day_line_margin + day_line_length - 1,
                       line_y),
                      fill=(255, 0, 0), width=1)

        if year < int(day['date'][0:4]):
            print_new_year(draw, year, line_y, img_width - 2 * margin)
            draw.line((margin - day_line_margin,
                       line_y,
                       img_width - margin,
                       line_y),
                      fill=(0, 0, 255), width=1)
            year += 1

        day_increment += 1

    img.save('covid.png')


def main():
    req = urllib.request.Request("https://www.data.gouv.fr/fr/datasets/r/d2671c6c-c0eb-4e12-b69a-8e8f87fc224c")
    full_data = []

    try:
        response = urllib.request.urlopen(req)
    except HTTPError as e:
        print('Service indisponible.')
        print('Erreur : ', e.code)
        exit(0)
    except URLError as e:
        print('Serveur inaccessible.')
        print('Erreur : ', e.reason)
        exit(0)

    with response as json_file:
        json_data = json.load(json_file)

    for day in json_data:

        if day.get("decesEhpad") is not None:
            total_deaths_ehpad = day["decesEhpad"]
        else:
            total_deaths_ehpad = 0

        date = day["date"]
        total_deaths = day["deces"] + total_deaths_ehpad

        if full_data:
            daily_deaths = total_deaths - full_data[-1]["total_deaths"]
        else:
            daily_deaths = total_deaths

        if len(full_data) >= 7:
            moving_average = calc_moving_average(full_data, 7)
        else:
            moving_average = daily_deaths

        date_data = {"date": date,
                     "daily_deaths": daily_deaths,
                     "total_deaths": total_deaths,
                     "moving_average": moving_average
                     }
        full_data.append(date_data.copy())

    generate_image(full_data)


if __name__ == '__main__':
    main()
    print("-- Temps d'exécution : %s secondes --" % (time.time() - start_time))
