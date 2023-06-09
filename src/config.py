import configparser

CONFIG_FILE = '../config/config.ini'


class Config:
    def __init__(self):
        self.config = configparser.RawConfigParser()
        self.config.read(CONFIG_FILE)

    def get(self, section, option):
        return self.config.get(section, option)
