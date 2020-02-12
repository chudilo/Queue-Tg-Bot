import os
from telegram_api import TgBot
from db_api import DataBase


class UzhkaBot(TgBot):
    def __init__(self, token, database):
        self.commands = {"/start": self.start,
                    "/info": self.info,}

        super().__init__(token, self.handleMessage)

        self.db = DataBase("postgres", "ubuntu")

    def handleMessage(self, message):
        try:
            self.offset = message['update_id'] + 1

            if message['message']['text'] in self.commands.keys():
                self.commands[message['message']['text']](message)

            else:
                r = self.sendMessage(message['message']['chat']['id'],
                                     message['message']['text'])

            self.db.writeMessage(message['message']['chat']['id'],
                                 message['message']['chat']['first_name'] + " " + message['message']['chat']['last_name'],
                                 message['message']['chat']['username'],
                                 message['message']['text'])

            #print("answer", r)
            print("message", message)
        except Exception as e:
            # TODO: logging exceptions
            print("exception:", e)

    def start(self, message):
        self.db.createUser(message['message']['chat']['id'], "Радостная собака")
        self.sendMessage(message['message']['chat']['id'], "THIS IS A TRIUMPH")

    def info(self, message):
        self.sendSticker(message['message']['chat']['id'], "CAADAgADAQADTpCiDaNuAUvXQvO8FgQ")


def main():
    token = os.environ['TEST_TOKEN']
    database = "database.db"

    bot = UzhkaBot(token, database)
    bot.run()


if __name__ == "__main__":
    main()