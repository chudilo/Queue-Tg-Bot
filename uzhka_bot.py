import os
from telegram_api import TgBot


class UzhkaBot(TgBot):
    def __init__(self, token, database):
        commands = {}

        super().__init__(token, commands)
        self.database = database

    def __start(self):
        pass

    def __info(self):
        pass


def main():
    token = os.environ['TELEGRAM_TOKEN']
    database = "database.db"

    bot = UzhkaBot(token, database)
    bot.run()


if __name__ == "__main__":
    main()