import configparser
import os
from ast import literal_eval


class Config:
    config = configparser.ConfigParser()

    def __init__(self, path, **kwargs):
        self.path = path
        self.kwargs = kwargs

    def check_path(self):
        return os.path.exists(self.path)

    def create(self,
               url='https://realty.yandex.ru/altayskiy_kray/kupit/kvartira/?page=20',
               roomfilters={'studio': True, '1': True, '2': True, '3': True, 'more': True},
               pricefilters={'min': 0, 'max': 0},
               xl_path='pyxl.xlsx',
               n_flow=2):
        self.config.add_section('Settings')
        self.config.set('Settings', 'url', f'{url}')
        self.config.set('Settings', 'roomfilters', f'{roomfilters}')
        self.config.set('Settings', 'pricefilters', f'{pricefilters}')
        self.config.set('Settings', 'xl_path', f'{xl_path}')
        self.config.set('Settings', 'n_flow', f'{n_flow}')

        with open(self.path, 'w') as config_file:
            self.config.write(config_file)

    def read(self):
        config = {}

        with open(self.path) as config_file:
            self.config.read_file(config_file)

        for section in self.config.sections():
            section_config = {}
            options = self.config.options(section)

            for option in options:
                section_config[option] = self.config.get(section, option)

            config[section] = section_config

        return config

    def get_data(self):
        if not self.check_path():
            self.create(self.kwargs)

        config = self.read()

        config['Settings']['roomfilters'] = literal_eval(config['Settings']['roomfilters'])
        config['Settings']['pricefilters'] = literal_eval(config['Settings']['pricefilters'])
        config['Settings']['n_flow'] = int(config['Settings']['n_flow'])

        return config
