import os
from telegram_api import TgBot


def main():
    token = os.environ['TEST_TOKEN']
    database = "database.db"

    bot = TgBot(token, database)
    bot.run()


if __name__ == "__main__":
    main()