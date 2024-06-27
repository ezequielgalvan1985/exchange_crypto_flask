import pickle

import pika

class WalletService():
    def __init__(self):
        try:
            self._connection= connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            self._channel = connection.channel()
            self._exchange_name = ''
            self._queue_name = 'withdraw-request'
            self._channel.queue_declare(queue=self._queue_name, durable=True)

        except Exception as e:
            raise e


    def send_withdraw_queue(self, _message):
        message_byte = pickle.dumps(_message)
        #self._channel.basic_publish(exchange='', routing_key='hello', body=_body)
        self._channel.basic_publish(exchange='',
                              routing_key=self._queue_name,
                              body=message_byte,
                              properties=pika.BasicProperties(
                                  delivery_mode=pika.DeliveryMode.Persistent
                              ))
        self._connection.close()

