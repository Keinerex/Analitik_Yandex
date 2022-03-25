from pars import Parser
from config import Config
import pandas as pd


class Analyze:
    def __init__(self, config_path):
        self.__path = Config('config.ini').get_data()['Settings']['xl_path']
        self.__data = Parser(config_path).get_data()

    def __to_frame(self):
        self.__frame = pd.DataFrame(self.__data).sort_values('rooms', axis=0).reset_index(drop=True)
        print(self.__frame)

    def __convert_sub(self, lst, n):
        return list(map(lambda x: x.split(', ')[n], lst))

    def __mean(self, lst):
        try:
            return round(sum(lst) / len(lst), 2)
        except:
            return None

    def __analyze(self):

        self.__to_frame()
        sub = set(self.__convert_sub(self.__data['address'], 0))
        sub = sub ^ set(self.__convert_sub(self.__data['address'], 1))
        sub.add('all')
        sub = sorted(list(sub))
        rooms = sorted(list(set(self.__data['rooms'])))
        rooms.append('all')
        self.__area_frame = pd.DataFrame({subj: {room: self.__mean([tup[4] for tup in self.__frame.itertuples() if
                                                                    (tup[2] == room or room == 'all') and (
                                                                                subj in tup[5] or subj == 'all')]) for
                                                 room in rooms} for subj in sub}).T
        self.__count_frame = pd.DataFrame({subj: {room: len([tup[1] for tup in self.__frame.itertuples() if
                                                             (tup[2] == room or room == 'all') and (
                                                                         subj in tup[5] or subj == 'all')]) for room in
                                                  rooms} for subj in sub}).T
        self.__price_frame = pd.DataFrame({subj: {room: self.__mean([tup[1] for tup in self.__frame.itertuples() if
                                                                     (tup[2] == room or room == 'all') and (
                                                                                 subj in tup[5] or subj == 'all')]) for
                                                  room in rooms} for subj in sub}).T

        print(self.__price_frame)

    def __write(self):
        with pd.ExcelWriter(self.__path) as writer:
            self.__frame.to_excel(writer, sheet_name='all', index=False)
            self.__price_frame.to_excel(writer, sheet_name='price', index=True)
            self.__count_frame.to_excel(writer, sheet_name='count', index=True)
            self.__area_frame.to_excel(writer, sheet_name='area', index=True)
            writer.save()

    def main(self):
        self.__analyze()
        self.__write()
