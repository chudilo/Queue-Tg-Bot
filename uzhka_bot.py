# -*- coding: utf-8 -*-
import os
from telegram_api import TgBot
from db_api import DataBase
import datetime

# self.sendSticker(message['message']['chat']['id'], "CAADAgADAQADTpCiDaNuAUvXQvO8FgQ")

#my_reply_markup = {"inline_keyboard":
#                       [[{'text': "hello", 'callback_data': (str(datetime.datetime.now().timestamp()) + "  Quser_to_remove")}]]}

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

casual_markup = {"resize_keyboard": True, "keyboard":
                [[{"text": "/help"}, {"text": "/nick"}, {"text": "/info"}],
                [{"text": "/come"}, {"text": "/leave"}],
                [{"text": "/setcount"}]]}

number_markup = {"resize_keyboard": True, "keyboard":
                [[{"text": "1"}, {"text": "2"}, {"text": "3"}],
                [{"text": "4"}, {"text": "5"}, {"text": "6"}],
                [{"text": "7"}, {"text": "8"}, {"text": "9"}],
                [{"text": "0"}]]}

closed_message = "Южка спит и детки спят\nЗавтра пампить захотят"

class UzhkaBot(TgBot):
    def __init__(self, token, database, user):
        self.commands = {"/start": self.start,
                    "/info": self.info,
                    "/come": self.come,
                    "/leave": self.leave,
                    "/setcount": self.setCount,
                    "/nick": self.setNickname,
                    "/help": self.help,
        }

        super().__init__(token, self.handleMessage)

        self.schedule = {0:(7,21), 1:(7,21), 2:(7,21),
                         3:(7,21), 4:(7,22), 5:(7,22), 6:(7,21),}

        self.db = DataBase(database, user)

    def isClosed(self):
        today =  datetime.datetime.now().weekday()
        time = datetime.datetime.time(datetime.datetime.now())
        
        print(self.schedule[today][0], time.hour, self.schedule[today][1])
        if self.schedule[today][0] <= time.hour < self.schedule[today][1]:
            print("FFFFFFf")
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
            self.offset = message['update_id'] + 1

            if not self.isRegistered(message['message']['chat']['id']):
                self.createUser(message['message']['chat']['id'])

            self.saveLog(message)

            if message['message']['text'] in self.commands.keys():
                self.commands[message['message']['text']](message)
            else:
                self.handleSplitCommands(message)
        except Exception as e:
            print(e)

    def handleSplitCommands(self, message):
        chat_id = message['message']['chat']['id']
        text = message['message']['text'].strip()

        if self.db.getFlag(chat_id, "set_count"):
            if text.isdigit():
                #print(self.db.getQueue(), int(text))
                if len(self.db.getQueue()) <= int(text) :
                    self.db.setCount(int(text))
                    self.db.clrUserFlag(chat_id, "set_count")
                    self.answerToUser(chat_id, self.infoMessage(), casual_markup)
                else:
                    self.db.setCount(len(self.db.getQueue()))
                    self.db.clrUserFlag(chat_id, "set_count")
                    self.answerToUser(chat_id, "Последний кораблик уплыл\nПоследний кабанчик устал...", casual_markup)
                    self.answerToUser(chat_id, self.infoMessage(), casual_markup)
            else:
                self.answerToUser(chat_id, "Неверный формат ввода, попробуйте ещё раз")

        elif self.db.getFlag(chat_id, "nickname"):
            if len(text) > 13:
                self.answerToUser(chat_id, "Слишком длинный вариант (макс. 13), попродуйте ещё раз")
                #self.answerToUser(message['message']['chat']['id'], "Добро пожаловать, ")
            elif text in self.db.getNicknames():
                self.answerToUser(chat_id, "Такое имя уже используется, попробуйте ещё раз")
            else:
                self.db.setNickname(chat_id, text)
                self.db.clrUserFlag(chat_id, "nickname")
                self.answerToUser(chat_id, "Добро пожаловать, " + text, casual_markup)
        else:
            self.answerToUser(message['message']['chat']['id'], message['message']['text'], casual_markup)

    def answerToUser(self, chat_id, text, reply_markup={}):
        #reply_markup = my_reply_markup
        self.db.writeMessage(chat_id, "PUMP_BOT", None, text)
        self.sendMessage(chat_id, text, reply_markup)

    def help(self, message):
        self.answerToUser(message['message']['chat']['id'], help_message())

    def start(self, message):
        self.answerToUser(message['message']['chat']['id'], help_message())
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
                                 "Добро пожаловать, снова.\n" + self.infoMessage(check=True), casual_markup)
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
                                  "Пока-пока!\n" + self.infoMessage(check=True), casual_markup)
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
            answer += "\n" + ", ".join(map(str, [row[0] for row in queue]))

        if check:
            answer += "\n\nНе забудь сверить информацию\n" + "(* ^ ω ^)"
        elif time:
            time += datetime.timedelta(hours=3)
            answer += "\nПоследнее обновление: " + time.strftime("%H:%M")

        return answer


def main():
    token = os.environ['TELEGRAM_TOKEN']
    database = "pump_bot"
    user = "ubuntu"

    bot = UzhkaBot(token, database, user)
    bot.run()


if __name__ == "__main__":
    main()
