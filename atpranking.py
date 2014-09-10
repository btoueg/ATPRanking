# -*- coding: utf-8 -*-

import csv
import threading
import requests
from bs4 import BeautifulSoup


def get_dates():
    response = requests.get("http://www.atpworldtour.com/Rankings/Singles.aspx")
    soup = BeautifulSoup(response.text)
    options = soup.find(id="singlesDates").find_all("option")
    return [option.text for option in options]


def parse_rankings(html_page):
    soup = BeautifulSoup(html_page)
    atp_ranking_table = soup.find("table", class_="bioTableAlt")
    atp_ranking_tr_all = atp_ranking_table.find_all("tr")[1:] if atp_ranking_table else []

    for atp_ranking_tr in atp_ranking_tr_all:
        split_text = atp_ranking_tr.find("td").text.strip().split()
        rank, player, country = split_text[0], " ".join(split_text[1:-1]), split_text[-1][1:-1]
        yield {
            'rank': rank,
            'player': player,
            'country': country,
        }


def get_rankings(params):
    response = requests.get("http://www.atpworldtour.com/Rankings/Singles.aspx", params=params)
    print(response.url, response.status_code)
    for ranking in parse_rankings(response.text):
        ranking['date'] = params['d']
        with threading.Lock():
            csv_writer.writerow(ranking)

retry_urls = [
    {"r": "401", "d": "05.08.2013"},
    {"r": "1", "d": "26.05.2014"},
    {"r": "301", "d": "09.04.2001"},
    {"r": "301", "d": "21.02.2000"},
    {"r": "401", "d": "12.08.2013"},
    {"r": "401", "d": "16.06.2014"},
    {"r": "1", "d": "04.04.2005"},
    {"r": "1", "d": "13.04.1998"},
    {"r": "1", "d": "21.10.1996"},
    {"r": "301", "d": "02.11.1987"},
    {"r": "101", "d": "21.09.2009"},
    {"r": "1", "d": "18.06.2001"},
    {"r": "401", "d": "06.06.2005"},
    {"r": "101", "d": "12.05.2014"},
    {"r": "201", "d": "22.07.2013"},
    {"r": "301", "d": "21.09.2009"},
    {"r": "101", "d": "05.03.1975"},
]

csv_file = open("atp_men_singles_ranking_retry2.csv", "w", newline='')
csv_writer = csv.DictWriter(csv_file, fieldnames=['date', 'rank', 'player', 'country'])

atp_singles_dates = get_dates()
for param in retry_urls:
        threading.Thread(target=lambda: get_rankings(param)).start()