import configparser
import os
from ast import literal_eval


class Config:
    __config = configparser.ConfigParser()

    def __init__(self, path, **kwargs):
        self.__path = path
        self.__kwargs = kwargs

    def __check_path(self):
        return os.path.exists(self.__path)

    def __create(self,
               url='https://realty.yandex.ru/altayskiy_kray/kupit/kvartira/?page=20',
               roomfilters={'studio': True, '1': True, '2': True, '3': True, 'more': True},
               pricefilters={'min': 0, 'max': 0},
               xl_path='pyxl.xlsx',
               n_flow=2):
        self.__config.add_section('Settings')
        self.__config.set('Settings', 'url', f'{url}')
        self.__config.set('Settings', 'roomfilters', f'{roomfilters}')
        self.__config.set('Settings', 'pricefilters', f'{pricefilters}')
        self.__config.set('Settings', 'xl_path', f'{xl_path}')
        self.__config.set('Settings', 'n_flow', f'{n_flow}')

        with open(self.__path, 'w') as config_file:
            self.__config.write(config_file)

    def __read(self):
        config = {}

        with open(self.__path) as config_file:
            self.__config.read_file(config_file)

        for section in self.__config.sections():
            section_config = {}
            options = self.__config.options(section)

            for option in options:
                section_config[option] = self.__config.get(section, option)

            config[section] = section_config

        return config

    def get_data(self):
        if not self.__check_path():
            self.__create(self.__kwargs)

        config = self.__read()

        config['Settings']['roomfilters'] = literal_eval(config['Settings']['roomfilters'])
        config['Settings']['pricefilters'] = literal_eval(config['Settings']['pricefilters'])
        config['Settings']['n_flow'] = int(config['Settings']['n_flow'])

        return config
