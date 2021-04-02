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
    """Calculates the average of the last n values in the data dictionary

    :param data: dictionary
    :param n: number of days used to calculate the moving average
    :return: integer value of the average
    """
    past_n_days = data[-n:]
    sum_values = 0
    for day in past_n_days:
        sum_values += day["daily_deaths"]
    n_moving_average = int(sum_values / n)
    return n_moving_average


def print_ten_thousand_text(draw, total_deaths, date, line_y, text_left):
    """Draws a line every 10000 deaths, the date and the total exact number of deaths at this date

    :param draw: ImageDraw object that will be the final output image
    :param total_deaths: integer
    :param date: date with format yyyy-mm-dd
    :param line_y: y coordinate of the line that is drawn
    :param text_left: x coordinate from which the text must be drawn
    :return: n/a
    """
    line_y -= 2
    ten_thousand_text_date = date
    ten_thousand_text_deaths = str(total_deaths)
    ten_thousand_text_date_width, ten_thousand_text_date_height = draw.textsize(ten_thousand_text_date,
                                                                                font=font_small)
    ten_thousand_text_deaths_width, ten_thousand_text_deaths_height = draw.textsize(ten_thousand_text_deaths,
                                                                                    font=font_regular)
    draw.text((text_left, line_y - ten_thousand_text_deaths_height - ten_thousand_text_date_height),
              ten_thousand_text_date,
              font=font_small,
              fill=(255, 0, 0))
    draw.text((text_left, line_y - ten_thousand_text_deaths_height),
              ten_thousand_text_deaths + " morts",
              font=font_regular,
              fill=(255, 0, 0))


def print_new_year(draw, year, line_y, year_left):
    """Draws a line when a new year is beginning and writes the years

    :param draw: ImageDraw object that will be the final output image
    :param year: year that is ending
    :param line_y: y coordinate of the line that is drawn
    :param year_left: x coordinate from which the text with the year must be drawn
    :return: n/a
    """
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
    """Generates the image output from the data collected

    :param data: dictionary that contains all data, formatted and ready to be used to draw the image output
    :return: n/a
    """

    # Variables used to set the layout. Small changes are generally fine.
    nb_days = len(data)
    margin = 15
    max_moving_average = max(item['moving_average'] for item in data)
    margin_top = 50
    margin_bottom = 30
    margin_right = 6 * margin
    line_multiplier = 2  # set a higher number to have a thinner, more vertical output (careful: might break layout)
    day_line_length = 3
    day_line_margin = 2
    ten_thousand_deaths_length = 3 * margin

    img_height = line_multiplier * nb_days + margin_top + margin_bottom + 2 * margin
    img_width = int(max_moving_average / line_multiplier) + 2 * margin + margin_right
    text_left = img_width - margin_right
    img = Image.new(mode="RGB", size=(img_width, img_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Main title of the graph
    title = "MORTS DU COVID-19 EN FRANCE DU " + data[0]['date'] + " AU " + data[-1]['date']
    title_width, title_height = draw.textsize(title, font=font_regular)

    # Subtitle to give secondary information
    sub_title_1 = "1 pixel noir = 1 décès"
    sub_title_1_width, sub_title_1_height = draw.textsize(sub_title_1, font=font_regular)
    sub_title_2 = "Décès lissés sur 7 jours"

    # Footer for credit information.
    footer_1 = "David Bertho"
    footer_2 = "bertho.eu/covid"
    source_1 = "Source : Ministère des Solidarités et de la Santé"
    source_2 = "data.gouv.fr"

    footer_1_width, footer_1_height = draw.textsize(footer_1, font=font_regular)
    footer_2_width, footer_2_height = draw.textsize(footer_2, font=font_regular)
    source_1_width, source_1_height = draw.textsize(source_1, font=font_regular)
    source_2_width, source_2_height = draw.textsize(source_2, font=font_regular)
    footer_width = max(footer_1_width, footer_2_width)

    draw.text(((img_width - title_width) / 2, 10),
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

        # loop to print victims in the image randomly
        while single_victim < day["moving_average"]:
            pixel_x = random.randint(margin,
                                     img_width - margin - margin_right - 1)
            pixel_y = random.randint(margin_top + margin + day_increment * line_multiplier,
                                     margin_top + margin + (day_increment + 1) * line_multiplier)
            # check if the pixel is already "dead" to avoid the superposition of victims
            if img.getpixel((pixel_x, pixel_y)) == (255, 255, 255):
                img.putpixel((pixel_x, pixel_y), (0, 0, 0))
                single_victim += 1

        # check if a multiple of 10k victime has passed
        # if so, a line is printed with the date and exact count
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

        # check if new year
        # if so, a line is printed with a text that shows both years
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

    '''
    this is the URL for a JSON file containing data for France
    change it with the URL of your choice
    the JSON file contains the following information used in this script:
    {
        "deces": 69596,
        "decesEhpad": 26044,
        "date": "2021-03-31"
    }
    deces and decesEhpad count the number of deaths respectively in general hospitals and nursing homes
    They must be added to have the total count of deaths
    '''

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

    # this loop parses each day of the JSON file and adds the relevant processed data in a new dictionary file
    for day in json_data:

        # during the first days of the pandemic, nursing home deaths were not included in the file
        # or were marked as "null"
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
