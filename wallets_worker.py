#!/usr/bin/env python
import threading
from datetime import timedelta, time

import pika
import json
from models import WalletContract
from flask import Flask, request
from db import db

app = Flask(__name__)

#
# Configuracion de la aplicacion FLASK
#
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

'''
el generador de wallets "generator-wallets.js, crea una wallet en  la blockchain 
y guarda en la cola wallets_queue
wallets_worker.py > escuchando la cola wallets_queue y guarda el registro en la tabla walletContract
'''


#
# Funcionalidad del worker
#
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

def on_message_callback(ch, method, properties, body):
    with app.app_context():
        try:
            dato_str = body.decode('utf-8')
            record_dict = json.loads(dato_str)
            m = WalletContract()
            m.address = record_dict['address']
            m.chain_id = record_dict['chain_id']
            m.reserved = record_dict['reserved']

            db.session.add(m)
            db.session.commit()
            app.logger.info("WalletContract Registrado ok "+ m.address)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            app.logger.error(e)


def worker():
    queue_name = 'wallets_queue'
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback,auto_ack=False)
    app.logger.info("Worker Wallets Queue Iniciado...")
    channel.start_consuming()




#
# metodos de la api
#
@app.route('/workers/iniciar', methods=['POST'])
def worker_iniciar():
    try:
        if not new_t.is_alive():
            new_t.start()
            return {"data":"consumidor iniciado"}
        return {"data": "ya se encuentra activo"}

    except Exception as e:
        app.logger.error(e)


@app.route('/workers/detener', methods=['POST'])
def worker_detener():
    try:
        channel.stop_consuming()
        return {"data":"consumidor detenido"}
    except Exception as e:
        app.logger.error(e)


@app.route('/workers/test', methods=['POST'])
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


new_t = threading.Thread(target=worker, name="worker")
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=3000,debug=True)