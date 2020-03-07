# Telegram-Queue-Bot

https://t.me/PumpStatBot

Бот для сбора статистики посещений и контроля очереди на танцевально-игровом автомате.

### Инструменты

1. Бот написан на языке *python*, работа с API Telegram реализована с помощью библиотеки *requests*.
2. Работа с базами данных (*sqlite*, позднее переехал на *postgresql*).
3. (WIP) *nginx* и веб сервер на *Flask* и для использования Telegram WebHook.
4. Хост на облачном сервере amazon lightsail (*systemd*, *cron*).


### Команды

Для запуска:

`$ python3 uzhka_bot.py`

Создание таблиц:

`$ python3 db_api.py init`

Ночной сброс:

`$ python3 db_api.py reset`