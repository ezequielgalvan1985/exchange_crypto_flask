#!/usr/bin/env python
import pickle

import pika
import httpx


def fnCallback(ch, method, properties, body):
    try:

        json_data = pickle.loads(body)
        #dato_str = body.decode('utf-8')
        print("withdraw-request:",json_data )
    except Exception as e:
        print("Error en withdraw-request callback: "+ e.message)


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
exchange_name = ''
queue_name = 'withdraw-request'
channel.queue_declare(queue=queue_name, durable=True)
channel.basic_consume(queue=queue_name, on_message_callback=fnCallback,auto_ack=True)
print('... Worker Withdraw Request escuchando...')
channel.start_consuming()