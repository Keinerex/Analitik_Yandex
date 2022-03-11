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
        self.start_url = self.config['url'][2:-2]
        self.room_filters = self.config['roomfilters']
        self.price_filters = self.config['pricefilters']
        self.n_flow = self.config['n_flow']
        self.manager = multiprocessing.Manager().list()

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
        print(self.start_url)

        while True:
            print(self.urls[-1])
            html = self.get_response(self.urls[-1])
            if html.status_code == Html.Ok.value:
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

        self.cut_list()

    def create_data_dict(self):
        dict = {}
        dict['price'] = []
        dict['rooms'] = []
        dict['link'] = []
        dict['area'] = []
        dict['adress'] = []

        return dict

    def check_filters(self, room, price):
        one = room in self.room_filters
        if self.price_filters['max']:
            two = self.price_filters['min'] <= price <= self.price_filters['max']
        else:
            two = self.price_filters['min'] <= price

        return one and two

    def get_content(self, response, dict):
        html = bs(response.text, 'html.parser')
        script = html.find('script', id="initial_state_script").get_text()[23:-1]
        data = json.loads(script)
        for offer in data['map']['offers']['points']:
            if (rooms := offer['roomsTotalKey']) in [str(i) for i in range(4, 10)]:
                rooms = 'more'

            if self.check_filters(rooms, (price := offer['price']['value'])):
                dict['price'].append(price)
                dict['rooms'].append(offer['roomsTotalKey'])
                dict['link'].append(offer['shareUrl'])
                dict['area'].append(offer['area']['value'])
                dict['adress'].append(
                    offer['location']['structuredAddress']['component'][-2]['address'] + ', ' +
                    offer['location']['structuredAddress']['component'][-1]['address'])

        return dict

    def parse(self, urls):
        for url in urls:
            self.manager.append(self.get_content(self.get_response(url), self.create_data_dict()))
        print(self.manager)

    def main(self):
        self.pagination()
        print(self.cut_urls)
        self.parse(self.cut_urls[0])