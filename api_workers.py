#!/usr/bin/env python
import threading
from datetime import timedelta
import pika
import json
from models import WalletContract
from schemas import WalletContractSchema
from flask import Flask, request
from db import db
from workers import WalletWorker

app = Flask(__name__)

SECRET_KEY = '123447a47f563e90fe2db0f56b1b17be62378e31b7cfd3adc776c59ca4c75e2fc512c15f69bb38307d11d5d17a41a7936789'
PROPAGATE_EXCEPTIONS = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SHOW_SQLALCHEMY_LOG_MESSAGES = False
ERROR_404_HELP = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['PROPAGATE_EXCEPTIONS'] = PROPAGATE_EXCEPTIONS
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SHOW_SQLALCHEMY_LOG_MESSAGES'] = SHOW_SQLALCHEMY_LOG_MESSAGES
app.config['ERROR_404_HELP'] = ERROR_404_HELP

db.init_app(app)




#funcion de testo

@app.route('/workers/wallets-queue', methods=['POST'])
def test_wallets_queue():
    try:
        json_string = json.dumps(request.get_json())
        json_byte = json_string.encode('utf-8')

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        queue_name = 'wallets_queue'
        channel.queue_declare(queue=queue_name, durable=True)

        channel.basic_publish(exchange='',
                              routing_key='wallets_queue',
                              body=json_byte)
        return {"data":json_string}
    except Exception as e:
        app.logger.error(e)


lista_workers=[]
@app.route('/workers/iniciar', methods=['POST'])
def iniciar_worker():
    try:
        w = WalletWorker(app)
        t = threading.Thread(target=w.run(), name="worker")
        #t.start()
        lista_workers.append(t)
        return {"data":"iniciado"}
    except Exception as e:
        app.logger.error(e)



if __name__ == '__main__':
    app.run(host="127.0.0.1", port=3000,debug=True)