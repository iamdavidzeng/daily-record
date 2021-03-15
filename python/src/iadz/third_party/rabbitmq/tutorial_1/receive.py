# -*- coding: utf-8 -*-


import pika


connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()

channel.queue_declare(queue="hello")


def callback(ch, method, properties, body):
    print("[x] Received %s" % body)


channel.basic_consume(queue="hello", on_message_callback=callback, auto_ack=True)

print("[*] Waiting for messages. to exist proee CTRL+C")
channel.start_consuming()
