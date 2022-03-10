from config import Config

if __name__ == '__main__':
    config = Config('config.ini')
    print(config.get_data())
