#!/usr/bin/env python
import pika
import httpx



def post_create_wallet(json_body):
    try:
        host = "http://localhost:5000/app-core/v1/wallet-contract/?format=json"
        response = httpx.post(host,
                              data=json_body,
                              headers={"Content-Type": "application/json"},
                              )
        print(response.json())
    except :
        print("error en post_create_wallet: ")

def wallets_queue_callback(ch, method, properties, body):
    try:
        print("wallets_queue_callback")
        dato_str = body.decode('utf-8')
        post_create_wallet(dato_str)
    except Exception as e:
        print("Error en wallets_queue_callback: "+ e.message)


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
exchange_name = ''
queue_name = 'wallets_queue'
channel.queue_declare(queue=queue_name, durable=True)
channel.basic_consume(queue=queue_name, on_message_callback=wallets_queue_callback,auto_ack=True)
print('... Worker Wallets Queue escuchando...')
channel.start_consuming()