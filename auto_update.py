import os
import requests
import datetime
from uzhka_bot import UzhkaBot

import logging

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(filename='/logs/auto_update.log', level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__name__)


token = os.environ['TELEGRAM_TOKEN']
database = "pump_bot"
user = "ubuntu"
bot = UzhkaBot(token, database, user)


def get_tracked_people(bot):
    cur = bot.db.connection.cursor()
    cur.execute('''SELECT chat_id, piu_nick FROM users
                   WHERE piu_nick IS NOT null;
                ''')
    return cur.fetchall()


def get_plays(bot=None):
    tracked_people = get_tracked_people(bot)
    tracked_people = {k: v for v, k in tracked_people}
    print(tracked_people)

    ukro_url = os.environ.get('UKRO_URL')

    resp = requests.get(ukro_url, verify=False)
    print(resp)
    results = resp.json().get('lastResults')
    print(results)

    for nick in results.keys():
        tracked_nicknames = tracked_people.keys()
        if nick in tracked_nicknames:
            now = datetime.datetime.now()
            played = datetime.datetime.strptime(results[nick], '%Y-%m-%d %H:%M:%S')
            if now - played < datetime.timedelta(minutes=10):
                message = {}
                message['message']['chat']['id'] = tracked_people[nick]
                bot.come(message)


if __name__ == '__main__':
    try:
        get_plays()
    except Exception as e:
        logger.error(e)
        raise
