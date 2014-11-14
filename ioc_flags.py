# -*- coding: utf-8 -*-

import csv
import requests
from bs4 import BeautifulSoup


csv_file = open("ioc_flags.csv", "w", newline='')
csv_writer = csv.DictWriter(csv_file, fieldnames=['code', 'url'])


def get_country_flags():
    response = requests.get("http://en.wikipedia.org/wiki/List_of_IOC_country_codes")
    soup = BeautifulSoup(response.text)
    wikitables = soup.find_all(class_="wikitable")
    for wikitable in wikitables:
        for tr in wikitable.find_all("tr"):
            td = tr.find_all("td")
            if td:
                country_code = td[0].text
                img = td[2].find("img")
                if img:
                    url = img.get("src").replace("22px", "200px")
                    csv_writer.writerow({'code': country_code, 'url': url})
                if country_code == "ZIM":
                    return

get_country_flags()
