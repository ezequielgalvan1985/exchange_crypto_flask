#!/usr/bin/env python
import threading
from datetime import timedelta
from datetime import date
import pika
import json
from models import WalletContract, Transaction, Wallet
from schemas import WalletContractSchema
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
app.config['PROPAGATE_EXCEPTIONS'] = PROPAGATE_EXCEPTIONS
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SHOW_SQLALCHEMY_LOG_MESSAGES'] = SHOW_SQLALCHEMY_LOG_MESSAGES
app.config['ERROR_404_HELP'] = ERROR_404_HELP
db.init_app(app)



'''
Descripcion de Proceso Worker:
escucha la cola eth-transaccions
lee la wallet a la cual se hizo el deposito
genera un registro en la tabla Transaccion 
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
            d = json.loads(dato_str)

            #dar de alta el modelo
            w = Wallet.query.filter_by(chain_id = d['chain_id'],
                                       address=d['wallet_address'],
                                       coin=d['coin']).first()
            if not w is None:
                t = Transaction()
                t.tx_hash = d['tx_hash']
                t.nature = 1
                t.amount = 0
                t.created_at = date.today()
                t.wallet = w
                db.session.add(t)
                db.session.commit()
                app.logger.info("ModeloName Registrado ok ")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                app.logger.warning("No existe wallet, por lo tanto no se pudo registrar la transaccion ")

        except Exception as e:
            app.logger.error(e)

def worker():
    queue_name = 'eth-transactions'
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback,auto_ack=False)
    app.logger.info("Worker eth-transactions Queue escuchando...")
    channel.start_consuming()

#
# metodos de la api
#
@app.route('/workers/iniciar', methods=['POST'])
def worker_iniciar():
    try:
        if not new_t.is_alive():
            new_t.start()
        else:
            channel.start_consuming()

        app.logger.info("Worker eth-transactions INICIADO")
        return {"data":"consumidor iniciado"}
    except Exception as e:
        app.logger.error(e)
        return {"data": "error al querer iniciar el worker"}


@app.route('/workers/detener', methods=['POST'])
def worker_detener():
    try:
        channel.stop_consuming()
        app.logger.info("Worker eth-transactions DETENIDO")
        return {"data":"consumidor detenido"}
    except Exception as e:
        app.logger.error(e)


@app.route('/workers/test', methods=['POST'])
def test_queue():
    try:
        json_string = json.dumps(request.get_json())
        json_byte = json_string.encode('utf-8')

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        queue_name = 'eth-transactions'
        channel.queue_declare(queue=queue_name, durable=True)

        channel.basic_publish(exchange='',
                              routing_key='eth-transactions',
                              body=json_byte)
        return {"data":json_string}
    except Exception as e:
        app.logger.error(e)


new_t = threading.Thread(target=worker, name="worker")
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=3000, debug=True)