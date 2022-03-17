import math
import requests
from bs4 import BeautifulSoup as bs
import multiprocessing
import json
from config import Config
from enum import Enum
import sys


class Parser:
    def __init__(self, config_path):
        self.__config = Config(config_path)
        self.__config = self.__config.get_data()['Settings']
        self.__start_url = self.__config['url'][2:-2]
        self.__room_filters = self.__config['roomfilters']
        self.__price_filters = self.__config['pricefilters']
        self.__n_flow = self.__config['n_flow']
        self.__manager = multiprocessing.Manager().list()

    def __get_response(self, url):
        r = requests.get(url)
        r.encoding = 'utf-8'
        return r

    def __cut_list(self):
        self.__cut_urls = []
        N = math.ceil(len(self.__urls) / self.__n_flow)
        help_list = []
        for count, url in enumerate(self.__urls):
            help_list.append(url)

            if (count + 1) % N == 0 or count == len(self.__urls) - 1:
                self.__cut_urls.append(help_list)
                help_list = []

    def __pagination(self):
        self.__urls = [self.__start_url]

        while True:
            html = self.__get_response(self.__urls[-1])
            if html.status_code == 200:
                buttons = bs(html.text, 'html.parser')
                buttons = buttons.find('div', class_='Pager Pager_theme_islands OffersSerp__pager')
                buttons = buttons.findAll('a', class_='Pager__radio-link')

                if buttons[-1].get_text() == 'Следующая':
                    link = 'https://realty.yandex.ru' + (buttons[-1].get('href'))
                    self.__urls.append(link)
                else:
                    break
            else:
                sys.exit(html.status_code)

        self.__cut_list()

    def __check_filters(self, room, price):
        one = room in self.__room_filters
        if self.__price_filters['max']:
            two = self.__price_filters['min'] <= price <= self.__price_filters['max']
        else:
            two = self.__price_filters['min'] <= price

        return one and two

    def __get_content(self, response, dict):
        html = bs(response.text, 'html.parser')
        script = html.find('script', id="initial_state_script").get_text()[23:-1]
        data = json.loads(script)
        for offer in data['map']['offers']['points']:
            if (rooms := offer['roomsTotalKey']) in [str(i) for i in range(4, 10)]:
                rooms = 'more'

            if self.__check_filters(rooms, (price := offer['price']['value'])):
                dict['price'].append(price)
                dict['rooms'].append(offer['roomsTotalKey'])
                dict['link'].append(offer['shareUrl'])
                dict['area'].append(offer['area']['value'])
                dict['address'].append(', '.join(
                    map(lambda lst: lst['address'], offer['location']['structuredAddress']['component'][-4:-1])))

        return dict

    def parse(self, urls):
        for url in urls:
            self.__manager.append(self.__get_content(self.__get_response(url),
                                                     {i: [] for i in ['price', 'rooms', 'link', 'area', 'address']}))

    def __asynch(self):
        processes = []
        for urls in self.__cut_urls:
            processes.append(multiprocessing.Process(target=self.parse, args=(urls,)))

        for process in processes:
            process.start()
            process.join()

        for process in processes:
            process.close()
        self.__concat_dict()

    def __concat_dict(self):
        dct = {}
        for key in self.__manager[0].keys():
            lst = []
            for i in range(len(self.__manager)):
                lst.extend(self.__manager[i][key])
            dct[key] = lst
        self.__manager = dct

    def __main(self):
        self.__pagination()
        self.__asynch()

    def get_data(self):
        self.__main()
        return self.__manager
