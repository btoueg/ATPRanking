# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pprint

results = dict()


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
                results[country_code] = url
                if country_code == "ZIM":
                    return

get_country_flags()

pprint.pprint(results)
