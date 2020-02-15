# -*- coding: utf-8 -*-
import os
from telegram_api import TgBot
from db_api import DataBase
import datetime

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
                    "/nick": self.setNickname,
        }

        super().__init__(token, self.handleMessage)

        self.db = DataBase("postgres", "ubuntu")

    def saveLog(self, message):
        self.db.writeMessage(message['message']['chat']['id'],
                             message['message']['chat']['first_name'] + " " + message['message']['chat']['last_name'],
                             message['message']['chat']['username'],
                             message['message']['text'])

    def handleMessage(self, message):
        self.offset = message['update_id'] + 1

        if not self.isRegistered(message['message']['chat']['id']):
            self.createUser(message['message']['chat']['id'])

        self.saveLog(message)

        if message['message']['text'] in self.commands.keys():
            self.commands[message['message']['text']](message)
        else:
            self.handleSplitCommands(message)

    def handleSplitCommands(self, message):
        chat_id = message['message']['chat']['id']
        text = message['message']['text']

        if self.db.getFlag(chat_id, "set_count"):
            if text.isdigit():
                self.db.setCount(int(text))
                self.db.clrUserFlag(chat_id, "set_count")
                self.answerToUser(chat_id, self.infoMessage())
            else:
                self.answerToUser(chat_id, "Неверный формат ввода, попробуйте ещё раз")

        elif self.db.getFlag(chat_id, "nickname"):
            if len(text) <= 13:
                self.db.setNickname(chat_id, text)
                self.db.clrUserFlag(chat_id, "nickname")
                self.answerToUser(chat_id, "Добро пожаловать, " + text)
            else:
                self.answerToUser(chat_id, "Слишком длинный вариант (макс. 13), попродуйте ещё раз")
                #self.answerToUser(message['message']['chat']['id'], "Добро пожаловать, ")

        else:
            self.answerToUser(message['message']['chat']['id'], message['message']['text'])

    def answerToUser(self, chat_id, text, reply_markup={}):
        self.db.writeMessage(chat_id, "PUMP_BOT", None, text)
        self.sendMessage(chat_id, text, reply_markup)

    def start(self, message):
        self.answerToUser(message['message']['chat']['id'], help_message())
        self.answerToUser(message['message']['chat']['id'], "Введите свой никнейм:")

    def info(self, message):
        self.answerToUser(message['message']['chat']['id'], self.infoMessage())

    def come(self, message):
        if self.db.setUserFlag(message['message']['chat']['id'], "presence"):
            self.db.incCount()

        self.answerToUser(message['message']['chat']['id'], "ДАРОВА")

    def leave(self, message):
        if self.db.clrUserFlag(message['message']['chat']['id'], "presence"):
            self.db.decCount()

        self.answerToUser(message['message']['chat']['id'], "ПОКЕДА")

    def setCount(self, message):
        self.db.setUserFlag(message['message']['chat']['id'], "set_count")
        self.db.clrUserFlag(message['message']['chat']['id'], "nickname")
        self.answerToUser(message['message']['chat']['id'], "Напишите количество людей:")

    def setNickname(self, message):
        self.db.setUserFlag(message['message']['chat']['id'], "nickname")
        self.db.clrUserFlag(message['message']['chat']['id'], "set_count")
        self.answerToUser(message['message']['chat']['id'], "Напишите ваш новый ник:")

    def isRegistered(self, chat_id):
        if self.db.getUser(chat_id):
            return True
        else:
            return False

    def createUser(self, chat_id):
        self.db.createUser(chat_id)

    def infoMessage(self):
        count = self.db.getCount()
        queue = self.db.getQueue()
        time = self.db.getLastUpdate() + datetime.timedelta(hours=3)

        answer = """Количество людей на локации: {}\n{}
Последнее обновление: {}""".format(count, ", ".join(map(str, [row[0] for row in queue])),
                                   time.strftime("%H:%M"))
        return answer

def main():
    token = os.environ['TEST_TOKEN']
    database = "database.db"

    bot = UzhkaBot(token, database)
    bot.run()


if __name__ == "__main__":
    main()