from flask import Flask
import requests
import json

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>My page for TG</h1>'

URL = 'https://api.telegram.org/bot'
with open('token', 'r') as f:
    URL += f.read().strip()


def sendMessage(chat_id, text="Test message"):
    url = URL + 'sendMessage'
    r = requests.post(url, json={'chat_id': chat_id, 'text': text})
    return r.json()

def getMe():
    url = URL + 'getMe'
    r = requests.get(url)
    return r.json()


if __name__ == '__main__':
    #print(getMe())
    app.run()
