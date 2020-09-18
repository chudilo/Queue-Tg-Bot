from flask import Flask
from flask import request

import json
import requests


class TgBot(object):
    def __init__(self, token, handleMessage):
        self.token = token
        self.requestUrl = 'https://api.telegram.org/bot' + token
        self.offset = 0

        self.handleMessage = handleMessage

    def getMe(self):
        r = requests.get(self.requestUrl + '/getMe')
        return r.json()

    def getUpdates(self, timeout=0):
        print("offset:", self.offset)
        r = requests.post(self.requestUrl + '/getUpdates',
                          json={'offset': self.offset,
                                'timeout': timeout})
        return r.json()

    def sendMessage(self, chat_id, text, reply_markup=None):
        answer_json = {'chat_id': chat_id, 'text': text}
        if reply_markup:
            answer_json['reply_markup'] = reply_markup

        r = requests.post(self.requestUrl+'/sendMessage', json=answer_json)
        return r.json()

    def sendSticker(self, chat_id, sticker):
        r = requests.post(self.requestUrl + '/sendSticker',
                          json={'chat_id': chat_id,
                                'sticker': sticker})
        return r.json()

    # TODO: Make web hook bot
    def startWebHook(self):
        app = Flask(__name__)

        @app.route('/', methods=['POST'])
        def index():
            if request.method == 'POST':
                r = request.data.decode('unicode-escape')  # .decode("ascii").encode("utf-8").decode('unicode-escape')
                # print(json.dumps(json.loads(r), ensure_ascii=False, indent=4))
                print(r)

            return "correct"

        app.run(port='5000')

    def startGetUpdate(self):
        from uzhka_bot import logger
        while True:
            try:
                update = self.getUpdates(timeout=30)
                logger.debug(update)
                if update['ok']:
                    for message in update['result']:
                        self.handleMessage(message)
            except Exception as e:
                logger.error(e)

    def run(self, webHook=False):
        if webHook:
            self.startWebHook()
        else:
            self.startGetUpdate()
