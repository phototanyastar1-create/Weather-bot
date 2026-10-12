import time
import os
import requests
from threading import Thread
from flask import Flask

API_TOKEN = '8885818986:AAGTwtnX0sEiYiOHmiWuCChnmC1jQFBYBSc'
WEATHER_API_KEY = 'D246941f228ccd1e1af3055d307fd96c'

app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{API_TOKEN}/getUpdates"
    if offset:
        url += f"?offset={offset}"
    return requests.get(url).json()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

def telegram_bot():
    print("Telegram бот запущен...")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]
                    
                    if text == "/start":
                        send_message(chat_id, "Привет! Напиши название города, и я скажу погоду.")
                    else:
                        url = f"http://api.openweathermap.org/data/2.5/weather?q={text}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
                        resp = requests.get(url).json()
                        if resp.get("cod") == 200:
                            temp = resp["main"]["temp"]
                            desc = resp["weather"][0]["description"]
                            city_name = resp["name"]
                            ans = f"Погода в городе **{city_name}**:\n🌡 Температура: {temp}°C\n☁️ {desc.capitalize()}"
                            send_message(chat_id, ans)
                        else:
                            send_message(chat_id, "Город не найден. Проверь название и попробуй еще раз!")
        except Exception as e:
            print("Ошибка:", e)
        time.sleep(2)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    telegram_bot()
