# -*- coding: utf-8 -*-

import csv
from threading import Thread, Lock
from queue import Queue
import requests
from bs4 import BeautifulSoup

csv_file = open("atp_men_singles_ranking.csv", "w", newline='')
csv_writer = csv.DictWriter(csv_file, fieldnames=['date', 'rank', 'player', 'country', 'url', 'points', 'tournaments_played'])


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
        url = atp_ranking_tr.find("a").get('href')
        points = atp_ranking_tr.find_all("td")[1].text
        tournaments_played = atp_ranking_tr.find_all("td")[3].text
        yield {
            'rank': rank,
            'player': player,
            'country': country,
            'url': url,
            'points': points,
            'tournaments_played': tournaments_played
        }


def get_rankings(params):
    try:
        response = requests.get("http://www.atpworldtour.com/Rankings/Singles.aspx", params=params)
        if response.status_code != 200:
            print(response.status_code, params)
            return False
        print("ok")
        for ranking in parse_rankings(response.text):
            ranking['date'] = params['d']
            with Lock():
                csv_writer.writerow(ranking)
        return True
    except Exception as e:
        print(e)
        return False


def worker():
    while True:
        params = q.get()
        if not get_rankings(params):
            q.put(params)
        q.task_done()
        print(q.qsize())

q = Queue()
for i in range(6):
    t = Thread(target=worker)
    t.daemon = True
    t.start()


atp_singles_dates = get_dates()

for r in ("1", "101", "201", "301", "401"):
    for d in atp_singles_dates:
        q.put({"r": r, "d": d})

q.join()