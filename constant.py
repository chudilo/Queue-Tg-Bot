# -*- coding: utf-8 -*-
# self.sendSticker(message['message']['chat']['id'], "CAADAgADAQADTpCiDaNuAUvXQvO8FgQ")

# my_reply_markup = {"inline_keyboard":
#                       [[{'text': "hello",
#                       'callback_data': (str(datetime.datetime.now().timestamp()) + "  Quser_to_remove")}]]}


help_message = """Uzka Queue Bot v1.2.0\nИзвините, я упячко (I will fix it, probably)
    /help - вывести список команд
    /info - узнать количество человек на южке
    /nick - задать себе имя
    /stat - узнать статистику посещений
    /setcount - задать количество человек на локации
    /come - приехать на южку
    /leave - уехать с южки

По всем вопросам неопределенного поведения писать @chudikchudik"""


casual_markup = {"resize_keyboard": True, "keyboard":
                [[{"text": "/help"}, {"text": "/nick"}, {"text": "/info"}],
                [{"text": "/come"}, {"text": "/leave"}],
                [{"text": "/setcount"}]]}

number_markup = {"resize_keyboard": True, "keyboard":
                [[{"text": "1"}, {"text": "2"}, {"text": "3"}],
                [{"text": "4"}, {"text": "5"}, {"text": "6"}],
                [{"text": "7"}, {"text": "8"}, {"text": "9"}],
                [{"text": "0"}]]}

simple_markup = {"resize_keyboard": True, "keyboard":
                [[{"text": "/info"}],
                [{"text": "/come"}, {"text": "/setcount"}],
                [{"text": "/help"}, {"text": "/advanced"}],]}


simple_markup_leave = {"resize_keyboard": True, "keyboard":
                [[{"text": "/info"}],
                [{"text": "/leave"}, {"text": "/setcount"}],
                [{"text": "/help"}, {"text": "/advanced"}],]}

advanced_markup = {"resize_keyboard": True, "keyboard":
                [[{"text": "/info"}],
                [{"text": "/come"}, {"text": "/setcount"}],
                [{"text": "/nick"}, {"text": "/stat"}],
                [{"text": "/help"}, {"text": "/simple"}],]}

advanced_markup_leave = {"resize_keyboard": True, "keyboard":
                [[{"text": "/info"}],
                [{"text": "/leave"}, {"text": "/setcount"}],
                [{"text": "/nick"}, {"text": "/stat"}],
                [{"text": "/help"}, {"text": "/simple"}],]}

closed_message = "Южка спит и детки спят\nЗавтра пампить захотят"
