from flask import Flask
from flask import request


class TgBot(object):
    def __init__(self, token, commands):
        self.token = token
        self.requestUrl = 'https://api.telegram.org/bot' + token
        self.commands = commands

    def getMe(self):
        r = requests.get(self.requestUrl + '/getMe')
        return r.json()

    def sendMessage(self, chat_id, text, reply_markup=None):
        pass

    def sendSticker(self):
        pass

    def setWebHook(self):
        pass

    def deleteWebHook(self):
        pass

    def handleMessage(self, message: 'json'):
        pass

    def run(self):
        app = Flask(__name__)

        @app.route('/', methods=['POST'])
        def index():
            if request.method == 'POST':
                r = request.data.decode('unicode-escape')  # .decode("ascii").encode("utf-8").decode('unicode-escape')
                print(json.dumps(json.loads(r), ensure_ascii=False, indent=4))

            return "correct"

        app.run(port='5000')
