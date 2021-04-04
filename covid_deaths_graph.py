import urllib.request
from urllib.error import URLError, HTTPError
import json
import random
from PIL import Image, ImageDraw, ImageFont
import time
from sys import exit

start_time = time.time()
font_regular = ImageFont.truetype("asap.ttf", size=10)
font_small = ImageFont.truetype("asap.ttf", size=8)


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
    ten_thousand_text_deaths = str(int(total_deaths))
    ten_thousand_text_date_width, ten_thousand_text_date_height = draw.textsize(ten_thousand_text_date,
                                                                                font=font_small)
    ten_thousand_text_deaths_width, ten_thousand_text_deaths_height = draw.textsize(ten_thousand_text_deaths,
                                                                                    font=font_regular)
    draw.text((text_left, line_y - ten_thousand_text_date_height),
              ten_thousand_text_date,
              font=font_small,
              fill=(255, 0, 0))
    draw.text((text_left, line_y + 2),
              ten_thousand_text_deaths + " deaths",
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


def generate_image(data, location, region):
    """Generates the image output from the data collected

    :param data: dictionary that contains all data, formatted and ready to be used to draw the image output
    :param location: name of the country or region
    :param region: code of the country or region
    :return: n/a
    """
    # Variables used to set the layout. Small changes are generally fine.
    nb_days = len(data)
    margin = 15
    max_moving_average = max(item['moving_average'] for item in data) + 1
    margin_top = 60
    margin_bottom = 30
    margin_right = 7 * margin
    line_multiplier = 1
    day_line_length = 3
    day_line_margin = 2
    ten_thousand_deaths_length = 3 * margin

    img_width = 2000
    img_height = 1
    while img_width > 1900 or img_width * 1.5 > img_height:
        line_multiplier += 1
        img_width = max(round(max_moving_average / line_multiplier) + 2 * margin + margin_right, 500)
        img_height = line_multiplier * nb_days + margin_top + margin_bottom + 2 * margin
    text_left = img_width - margin_right
    img = Image.new(mode="RGB", size=(img_width, img_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Main title of the graph
    title = "DEATHS FROM COVID-19 IN " + location.upper() + " FROM " + data[0]['date'] + " TO " + data[-1]['date']
    title2 = "TOTAL: " + str(int(data[-1]["total_deaths"])) + " VICTIMS"
    title_width, title_height = draw.textsize(title, font=font_regular)
    title2_width, title2_height = draw.textsize(title2, font=font_regular)

    # Subtitle to give secondary information
    sub_title_1 = "1 black pixel = 1 victim"
    sub_title_1_width, sub_title_1_height = draw.textsize(sub_title_1, font=font_regular)
    sub_title_2 = "Deaths smoothed over 7 days"

    days = "Days"
    days_width, days_height = draw.textsize(days, font=font_regular)

    # Footer for credit information.
    footer_1 = "David Bertho"
    footer_2 = "bertho.eu/covid"
    source_1 = "Source : Our World in Data"
    source_2 = "ourworldindata.org/covid-deaths"

    footer_1_width, footer_1_height = draw.textsize(footer_1, font=font_regular)
    footer_2_width, footer_2_height = draw.textsize(footer_2, font=font_regular)
    source_1_width, source_1_height = draw.textsize(source_1, font=font_regular)
    source_2_width, source_2_height = draw.textsize(source_2, font=font_regular)
    footer_width = max(footer_1_width, footer_2_width)

    # draw title
    draw.text(((img_width - title_width) / 2, 10),
              title,
              font=font_regular,
              fill=(0, 0, 0))
    draw.text(((img_width - title2_width) / 2, 10 + title_height),
              title2,
              font=font_regular,
              fill=(0, 0, 0))

    # draw subtitle
    draw.text((margin, 10 + title_height * 3),
              sub_title_1,
              font=font_regular,
              fill=(0, 0, 0))
    if data[-1]["total_deaths"] > 5000:
        draw.text((margin,
                   10 + title_height * 3 + sub_title_1_height),
                  sub_title_2,
                  font=font_regular,
                  fill=(0, 0, 0))

    # draw day legend
    draw.text((img_width - margin - margin_right + day_line_margin,
               margin + margin_top - days_height),
              days,
              font=font_regular,
              fill=(255, 0, 0))

    # draw source information
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

    # draw credit information
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

    # show major lines depending on the total number of deaths
    if data[-1]["total_deaths"] > 1000000:
        multiplier = 500000
    elif data[-1]["total_deaths"] > 200000:
        multiplier = 100000
    elif data[-1]["total_deaths"] > 20000:
        multiplier = 10000
    elif data[-1]["total_deaths"] > 2000:
        multiplier = 1000
    elif data[-1]["total_deaths"] > 500:
        multiplier = 250
    elif data[-1]["total_deaths"] > 100:
        multiplier = 50
    elif data[-1]["total_deaths"] > 50:
        multiplier = 20
    else:
        multiplier = 10

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

        # check if a multiple of 10k victims has passed
        # if so, a line is printed with the date and exact count
        # for areas with over 200k victims, the multiplier is set to 100000 to improve legibility
        if int(day["total_deaths"] / multiplier) > ten_thousand_deaths:
            ten_thousand_deaths = int(day["total_deaths"] / multiplier)
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
        # print("daily victims printed")
        day_increment += 1

    img.save('covid_' + region.lower() + '.png')


def prepare_data(json_data, region):
    """

    :param json_data: json object containing all data
    :param region: region code to identify the country
    :return: fake return to exit the function if the country has no death data
    """
    location = json_data[region]["location"]
    full_data = []

    if not "total_deaths" in json_data[region]["data"][-1]:
        return None

    # this loop parses each day of the JSON file and adds the relevant processed data in a new dictionary file
    for day in json_data[region]["data"]:

        date = day["date"]
        if "new_deaths" in day:
            daily_deaths = day["new_deaths"]
        else:
            daily_deaths = 0

        if "total_deaths" in day:
            total_deaths = day["total_deaths"]
        else:
            total_deaths = 0

        # do not calculate the moving average for countries with very few deaths
        if len(full_data) >= 7 and json_data[region]["data"][-1]["total_deaths"] > 5000:
            moving_average = calc_moving_average(full_data, 7)
        else:
            moving_average = daily_deaths

        date_data = {"date": date,
                     "daily_deaths": daily_deaths,
                     "total_deaths": total_deaths,
                     "moving_average": moving_average
                     }
        full_data.append(date_data.copy())

    generate_image(full_data, location, region)
    print(location + " exported")


def main():
    """
    this is the URL for a JSON file maintained by Our World in Data containing data for all countries and regions
    change it with the URL of your choice
    """
    # set the region for which you want to create the graph
    # exemples: France: FRA, United Kingdom: GBR, Taiwan: TWN, European Union: OWID_EUN, World: OWID_WRL ...
    # to create graphs for each country and region, set this value to "all_countries"
    region = "all_countries"

    req = urllib.request.Request(
        "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.json")

    try:
        response = urllib.request.urlopen(req)
    except HTTPError as e:
        print('Service unavailable.')
        print('Error : ', e.code)
        exit(0)
    except URLError as e:
        print('Server unreachable.')
        print('Error : ', e.reason)
        exit(0)
    print("JSON downloaded")

    with response as json_file:
        json_data = json.load(json_file)

    if region == "all_countries":
        for country in json_data:
            prepare_data(json_data, country)
    else:
        prepare_data(json_data, region)


if __name__ == '__main__':
    main()
    print("-- Execution time: %s seconds --" % (time.time() - start_time))
