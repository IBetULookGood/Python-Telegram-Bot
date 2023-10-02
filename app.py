import os
import sys

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')

sys.path.append(vendor_dir)

from flask import Flask, request 
import requests
from dotenv import load_dotenv
from os.path import join, dirname
from yookassa import Configuration, Payment
import json

app = Flask(__name__)


def create_invoice():
    Configuration.account_id = get_from_env("SHOP_ID")
    Configuration.secret_key = get_from_env("PAYMENT_TOKEN")

    payment = Payment.create({
        "amount": {
            "value": "100.00",
            "currency": "RUB"
        },
        "configuration":{
            "type": "redirect",
            "return_url": "https://www.google.com"
        },
        "capture": True,
        "description" : "Заказ №1",
        "metadata":{"chat_id":chat_id}
    })
    return payment.confirmation.configuration_url

def get_from_env(key):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)


def send_message(chat_id, text):
    method = "sendMessage"
    token = get_from_env("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id" : chat_id, "text": text}
    requests.post(url, data=data)


def send_pay_button(chat_id, text):
    invoice_url = create_invoice(chat_id)

    method = "sendMessage"
    token = get_from_env("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/{method}"

    data = {"chat_id":chat_id, "text":text, "reply_markup":json.dumps({"inline_keyboard":[[{
        "text": "Оплатить!",
        "url": f"{invoice_url}"
    }]]})}

    request.post(url, data=data)


def check_if_successful_payment(request):
    try:
        if request.json["event"] == "payment.succeded":
           return True
    except KeyError:
            return False
    return False


@app.route('/', methods=["POST"])
def process():
    if check_if_successful_payment(request):
        # handling request from yookassa
        chat_id = request.json["object"]["metadata"]["chat_id"]
        send_message(chat_id, "Оплата прошла успешно!")
    else:
        # handling request Telegram
        chat_id = request.json["message"]["chat"]["id"]
        send_pay_button(chat_id=chat_id, text="Тестовая оплата")
        
    return {"ok":True}


if __name__ == '__main__':
    app.run()