import pars

if __name__ == '__main__':
    parser = pars.Parser('config.ini')
    print(parser.get_data())


