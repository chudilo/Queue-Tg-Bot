# -*- coding: utf-8 -*-
import os
import datetime
from telegram_api import TgBot
from db_api import DataBase
from constant import *

import logging

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(filename='/logs/pump_queries.log', level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__name__)


class UzhkaBot(TgBot):
    def __init__(self, token, database, user):
        self.commands = {"/start": self.start,
                         "/info": self.info,
                         "/come": self.come,
                         "/leave": self.leave,
                         "/setcount": self.setCount,
                         "/nick": self.setNickname,
                         "/help": self.help,
                         "/stat": self.stat,
        }

        super().__init__(token, self.handleMessage)

        self.schedule = {0:(7,21), 1:(7,21), 2:(7,21),
                         3:(7,21), 4:(7,22), 5:(7,22), 6:(7,21),}
        self.db = DataBase(database, user)

    def isClosed(self):
        today =  datetime.datetime.now().weekday()
        time = datetime.datetime.time(datetime.datetime.now())
        if self.schedule[today][0] <= time.hour < self.schedule[today][1]:
            return False
        else:
            return True

    def saveLog(self, message):
        keys = message['message']['chat'].keys()

        if 'username' in keys:
            username = message['message']['chat']['username']
        else:
            username = None

        name = ''
        if 'first_name' in keys:
            name += message['message']['chat']['first_name']

        if 'last_name' in keys:
            name += ' ' + message['message']['chat']['last_name']

        if name:
            name = name.strip()
        else:
            name = None
        self.db.writeMessage(message['message']['chat']['id'],
                             name,
                             username,
                             message['message']['text'])

    def handleMessage(self, message):
        try:
            logger.info(message)
            self.offset = message['update_id'] + 1

            if 'callback_query' in message.keys():
                print("HERE")
                self.pushOut(message['callback_query']['message']['chat']['id'],
                             message['callback_query']['data'])
            else:
                if not self.isRegistered(message['message']['chat']['id']):
                    self.createUser(message['message']['chat']['id'])

                self.saveLog(message)

                print("KEYS", message['message'].keys())


                if message['message']['text'] in self.commands.keys():
                    self.commands[message['message']['text']](message)
                else:
                    self.handleSplitCommands(message)
        except Exception as e:
            logger.error(e)

    def handleSplitCommands(self, message):
        chat_id = message['message']['chat']['id']
        text = message['message']['text'].strip()

        if self.db.getFlag(chat_id, "set_count"):
            if text.isdigit():
                #print(self.db.getQueue(), int(text))
                if int(text) > 25:
                    self.answerToUser(chat_id, "Вы тестировщик, попробуйте ещё раз")
                elif len(self.db.getQueue()) <= int(text) :
                    self.db.setCount(int(text))
                    self.db.clrUserFlag(chat_id, "set_count")
                    self.answerToUser(chat_id, self.infoMessage(), casual_markup)

                else:
                    if int(text) == 0:
                        self.db.clrUserFlag(chat_id, "presence")

                    self.db.setCount(len(self.db.getQueue()))
                    self.db.clrUserFlag(chat_id, "set_count")
                    #self.answerToUser(chat_id, "Последний кораблик уплыл\nПоследний кабанчик устал...", casual_markup)
                    queue = [row[0] for row in self.db.getQueue(chat_id=chat_id)]
                    if queue:
                        callback_reply_markup = {"inline_keyboard":
                                                     [
                            [{'text': name, 'callback_data': name } ] # (str(datetime.datetime.now().timestamp()))
                                                         for name in queue ]}

                        self.answerToUser(chat_id, self.infoMessage(), callback_reply_markup)
                        self.answerToUser(chat_id, "Вы можете выписать отсутствующих людей!", casual_markup)
                    else:
                        self.answerToUser(chat_id, self.infoMessage(), casual_markup)

            else:
                self.answerToUser(chat_id, "Неверный формат ввода, попробуйте ещё раз")

        elif self.db.getFlag(chat_id, "nickname"):
            new_nick = text.strip()
            if len(new_nick) > 13:
                self.answerToUser(chat_id, "Слишком длинный вариант (макс. 13), попробуйте ещё раз")
                #self.answerToUser(message['message']['chat']['id'], "Добро пожаловать, ")
            elif new_nick in self.db.getNicknames():
                self.answerToUser(chat_id, "Такое имя уже используется, попробуйте ещё раз")
            elif True in (char in {',', '.', ';', ':'} for char in new_nick):
                self.answerToUser(chat_id, "Недопустимый символ, попробуйте ещё раз")
            else:
                self.db.setNickname(chat_id, new_nick)
                self.db.clrUserFlag(chat_id, "nickname")
                self.answerToUser(chat_id, "Добро пожаловать, " + text, casual_markup)
        else:
            #self.answerToUser(message['message']['chat']['id'], message['message']['text'], casual_markup)
            pass

    def answerToUser(self, chat_id, text, reply_markup=None):
        #reply_markup = my_reply_markup

        self.db.writeMessage(chat_id, "PUMP_BOT", None, text)
        self.sendMessage(chat_id, text, reply_markup)

    def help(self, message):
        self.answerToUser(message['message']['chat']['id'], help_message)

    def start(self, message):
        self.answerToUser(message['message']['chat']['id'], help_message)
        self.db.setUserFlag(message['message']['chat']['id'], "nickname")
        self.db.clrUserFlag(message['message']['chat']['id'], "set_count")
        self.answerToUser(message['message']['chat']['id'], "Введите свой никнейм:", casual_markup)

    def info(self, message):
        self.db.clrUserFlag(message['message']['chat']['id'], "nickname")
        self.db.clrUserFlag(message['message']['chat']['id'], "set_count")
        if not self.isClosed():
            self.answerToUser(message['message']['chat']['id'], self.infoMessage(), casual_markup)
        else:
            self.answerToUser(message['message']['chat']['id'], closed_message, casual_markup)

    def come(self, message):
        self.db.clrUserFlag(message['message']['chat']['id'], "nickname")
        self.db.clrUserFlag(message['message']['chat']['id'], "set_count")
        if not self.isClosed():
            if self.db.setUserFlag(message['message']['chat']['id'], "presence"):
                self.db.incCount()
                self.answerToUser(message['message']['chat']['id'],
                                 "Добро пожаловать, {}.\n\n".format(self.db.getNickName(message['message']['chat']['id'])) + self.infoMessage(check=True), casual_markup)
            else:
                self.answerToUser(message['message']['chat']['id'],
                                  "Я знаю, что ты ещё тут...)", casual_markup)
        else:
            self.answerToUser(message['message']['chat']['id'], closed_message, casual_markup)

    def leave(self, message):
        self.db.clrUserFlag(message['message']['chat']['id'], "nickname")
        self.db.clrUserFlag(message['message']['chat']['id'], "set_count")
        if not self.isClosed():
            if self.db.clrUserFlag(message['message']['chat']['id'], "presence"):
                self.db.decCount()
                self.answerToUser(message['message']['chat']['id'],
                                  self.infoMessage(check=True), casual_markup)
            else:
                self.answerToUser(message['message']['chat']['id'],
                                  "Но ты же ещё не приехал...(", casual_markup)
        else:
            self.answerToUser(message['message']['chat']['id'], closed_message, casual_markup)

    def setCount(self, message):
        if not self.isClosed():
            self.db.setUserFlag(message['message']['chat']['id'], "set_count")
            self.db.clrUserFlag(message['message']['chat']['id'], "nickname")
            self.answerToUser(message['message']['chat']['id'], "Напишите количество людей:", number_markup)
        else:
            self.answerToUser(message['message']['chat']['id'], closed_message)

    def setNickname(self, message):
        self.db.setUserFlag(message['message']['chat']['id'], "nickname")
        self.db.clrUserFlag(message['message']['chat']['id'], "set_count")
        self.answerToUser(message['message']['chat']['id'], "Напишите ваш новый ник:", casual_markup)

    def isRegistered(self, chat_id):
        if self.db.getUser(chat_id):
            return True
        else:
            return False

    def createUser(self, chat_id):
        self.db.createUser(chat_id)

    def infoMessage(self, check=False):
        count = self.db.getCount()
        queue = self.db.getQueue()
        time = self.db.getLastUpdate()

        answer = "Количество людей на локации: {}".format(count)

        if queue:
            answer += "\n"

            if len(queue) != count:
                answer += "Среди них: "

            answer += ", ".join(map(str, [row[0] for row in queue])) + "."

        if check:
            answer += "\n\nНе забудь сверить информацию\n" + "(* ^ ω ^)"
        elif time:
            time += datetime.timedelta(hours=3)
            answer += "\nПоследнее обновление: " + time.strftime("%H:%M")

        return answer

    def pushOut(self, masterChatId, slave):
        print("PUSH OUT", masterChatId, slave)
        slaveChatId = self.db.getUserChatId(slave)
        print(slaveChatId)
        masterNick = self.db.getNickName(masterChatId)
        print(masterNick)

        if self.db.clrUserFlag(slaveChatId, "presence"):
            self.db.decCount()
            self.answerToUser(slaveChatId, "Вас выписал из очереди " + masterNick, casual_markup)
            self.answerToUser(masterChatId, "{} спит, но вы выписали забывашку с:".format(slave))
        else:
            self.answerToUser(masterChatId, slave + " уже убежал...", casual_markup)

    def stat(self, message):
        chat_id = message['message']['chat']['id']
        days = self.db.getWeekDays(chat_id)
        if len(days) < 10:
            self.answerToUser(chat_id, "Слишком мало посещений...")
        else:
            week = ("пн", "вт", "ср", "чт", "пт", "сб", "вс")
            days = [day.weekday() for day in days]
            answer = [": ".join([week[i], str(days.count(i))]) for i in range(7)]
            self.answerToUser(chat_id, "Ваша статистика посещений по дням недели (всего {} раз):\n".format(len(days)) + "\n".join(answer))


def sendAll():
    token = os.environ['TELEGRAM_TOKEN']
    database = "pump_bot"
    user = "ubuntu"

    bot = UzhkaBot(token, database, user)
    text = """Сегодня прошло пол года с момента запуска этого бота.
Много вещей претерпели изменения, комьюнити южки тоже, а я все так же сижу и лампово набираю код по вечерам.

Несмотря на некоторую неоднозначность (Плейдей, дай доступ к БД!), бот пользуется спросом у своей аудитории. За пол года:
Сообщений отправлено: ~10к.
Люди отметились: 652 раза
Отметили длину очереди: 870 раз
Просмотрели info: 5842 раз

Спасибо тестерам 🐗 ☁  🍋, активным пользователям 🤖 👟 ⛹\u200d♂, людям, которые врываются в 0 и отмечают 6 человек 🐕, а также просто скромным обзорщикам очереди 🦊
 
Общая статистика посещений (по количеству и по загруженности) будет ниже.
Также есть возможность узнать свою статистику по дням недели с помощью команды /stat
Если кто-то хочет посмотреть что-то конкретное, добро пожаловать в личку.

По всем предложениям, а также вопросам неопределенного поведения, писать, как обычно: @chudikchudik

p.s. некоторое время будьте осторожны и воздержитесь от посещения мест скопления людей
"""
    text2 = 'https://i.imgur.com/5TdqRYL.png'
    text3 = 'https://i.imgur.com/YU02i9Z.png'

    for user in bot.db.getAllChatId():
        bot.sendMessage(user, text)
        bot.sendMessage(user, text2)
        bot.sendMessage(user, text3)


def main():
    token = os.environ['TELEGRAM_TOKEN']
    database = "pump_bot"
    user = "ubuntu"

    bot = UzhkaBot(token, database, user)
    bot.run()


if __name__ == "__main__":
    main()
