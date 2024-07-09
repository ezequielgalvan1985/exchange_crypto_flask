import json
import pika
from db import db
from models import WalletContract



class WalletWorker():
    def __init__(self, app):
        self.app = app

    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        queue_name = 'wallets_queue'
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_consume(queue=queue_name, on_message_callback=self.on_message_callback, auto_ack=False)
        self.app.logger.info("Worker Wallets Queue escuchando...")
        channel.start_consuming()

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
                app.logger.info("WalletContract Registrado ok " + m.address)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                app.logger.error(e)
