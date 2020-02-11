import os
from telegram_api import TgBot

class UzhkaBot(TgBot):
    def __init__(self, token, database):
        self.commands = {"/start": self.start,
                    "/info": self.info,}

        super().__init__(token, self.handleMessage)
        self.database = database

    def handleMessage(self, message):
        try:
            self.offset = message['update_id'] + 1

            if message['message']['text'] in self.commands.keys():
                self.commands[message['message']['text']](message)

            else:
                r = self.sendMessage(message['message']['chat']['id'],
                                     message['message']['text'])

            print("answer", r)
            print("message", message)
        except Exception as e:
            print("exception:", e)

    def start(self, message):
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