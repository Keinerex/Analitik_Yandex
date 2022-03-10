import math

import requests
from bs4 import BeautifulSoup as bs
import multiprocessing
from multiprocessing.pool import ThreadPool
import json
import os
from config import Config
from enum import Enum
import sys


class Html(Enum):
    Ok = 200
    Bad_Request = 401
    Forbidden = 403
    Not_Found = 404
    Request_timeout = 408
    Locked = 423
    Bad_Gateway = 502
    Gateway_Timeout = 504
    Connection_Timed_Out = 522


class Parser:
    def __init__(self, config_path):
        self.config = Config('config.ini')
        self.config = self.config.get_data()['Settings']
        self.start_url = self.config['url']
        self.room_filters = self.config['roomfilters']
        self.price_filters = self.config['pricefilters']
        self.n_flow = self.config['n_flow']

    def get_response(self, url):
        r = requests.get(url)
        r.encoding = 'utf-8'
        return r

    def cut_list(self):
        self.cut_urls = []
        N = math.ceil(len(self.urls) / self.n_flow)
        help_list = []
        for count, url in enumerate(self.urls):
            help_list.append(url)

            if (count + 1) % N == 0 or count == len(self.urls) - 1:
                self.cut_urls.append(help_list)
                help_list = []

    def __call__(self, *args, **kwargs):
        return self.cut_urls

    def pagination(self):
        self.urls = [self.start_url]

        while True:
            html = self.get_response(self.urls[-1])

            if html.status_code == Html.Ok:
                buttons = bs(html.text, 'html.parser')
                buttons = buttons.find('div', class_='Pager Pager_theme_islands OffersSerp__pager')
                buttons = buttons.findAll('a', class_='Pager__radio-link')

                if buttons[-1].get_text() == 'Следующая':
                    link = 'https://realty.yandex.ru' + (buttons[-1].get('href'))
                    self.urls.append(link)
                else:
                    break
            else:
                sys.exit(html.status_code)
