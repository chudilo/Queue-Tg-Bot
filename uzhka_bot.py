# -*- coding: utf-8 -*-
import os
from telegram_api import TgBot
from db_api import DataBase


# self.sendSticker(message['message']['chat']['id'], "CAADAgADAQADTpCiDaNuAUvXQvO8FgQ")

def help_message():
    string = """Uzka Queue Bot v1.1.5\nИзвините, я упячко (I will fix it, probably)
    /help - вывести список команд
    /info - узнать количество человек на южке
    /nick - задать себе имя
    /setcount - задать количество человек на локации
    /come - приехать на южку
    /leave - уехать с южки

По всем вопросам неопределенного поведения писать @chudikchudik"""
    return string


class UzhkaBot(TgBot):
    def __init__(self, token, database):
        self.commands = {"/start": self.start,
                    "/info": self.info,
                    "/come": self.come,
                    "/leave": self.leave,
                    "/setcount": self.setCount,
        }

        super().__init__(token, self.handleMessage)

        self.db = DataBase("postgres", "ubuntu")

    def saveLog(self, message):
        self.db.writeMessage(message['message']['chat']['id'],
                             message['message']['chat']['first_name'] + " " + message['message']['chat']['last_name'],
                             message['message']['chat']['username'],
                             message['message']['text'])

    def handleMessage(self, message):
       # try:
        self.offset = message['update_id'] + 1

        if not self.isRegistered(message['message']['chat']['id']):
            self.createUser(message['message']['chat']['id'])

        self.saveLog(message)

        if message['message']['text'] in self.commands.keys():
            self.commands[message['message']['text']](message)
        else:
            r = self.sendMessage(message['message']['chat']['id'],
                                 message['message']['text'])
        #except Exception as e:
            # TODO: logging exceptions
            #print("exception:", e)

    def answerToUser(self, chat_id, text, reply_markup={}):
        self.db.writeMessage(chat_id, "PUMP_BOT", None, text)
        self.sendMessage(chat_id, text, reply_markup)

    def start(self, message):
        self.answerToUser(message['message']['chat']['id'], help_message())
        self.answerToUser(message['message']['chat']['id'], "Введите свой никнейм:")

    def info(self, message):
        queue = self.db.getQueue()
        self.answerToUser(message['message']['chat']['id'], ", ".join(map(str, [row[0] for row in queue])))

    def come(self, message):
        self.db.setUserFlag(message['message']['chat']['id'], "presence")
        self.answerToUser(message['message']['chat']['id'], "ДАРОВА")

    def leave(self, message):
        self.db.clrUserFlag(message['message']['chat']['id'], "presence")
        self.answerToUser(message['message']['chat']['id'], "ПОКЕДА")

    def setCount(self, message):
        self.db.setUserFlag(message['message']['chat']['id'], "setcount")
        self.answerToUser(message['message']['chat']['id'], "Напишите количество людей:")

    def isRegistered(self, chat_id):
        print("Here")
        if self.db.getUser(chat_id):
            return True
        else:
            return False

    def createUser(self, chat_id):
        self.db.createUser(chat_id)



def main():
    token = os.environ['TEST_TOKEN']
    database = "database.db"

    bot = UzhkaBot(token, database)
    bot.run()


if __name__ == "__main__":
    main()