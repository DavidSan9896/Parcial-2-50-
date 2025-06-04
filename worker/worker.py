import pika
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect_to_rabbitmq():
    while True:
        try:
            credentials = pika.PlainCredentials('david', '9896')
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq',
                    credentials=credentials,
                    heartbeat=600
                )
            )
            return connection
        except Exception as e:
            logger.error(f"Connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)


def main():
    connection = connect_to_rabbitmq()
    channel = connection.channel()

    channel.queue_declare(queue='messages', durable=True)
    logger.info("Worker ready. Waiting for messages...")

    def callback(ch, method, properties, body):
        try:
            message = body.decode()
            logger.info(f"Processing message: {message}")

            with open('/app/messages/messages.log', 'a') as f:
                f.write(f"{time.ctime()}: {message}\n")

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    channel.basic_consume(
        queue='messages',
        on_message_callback=callback,
        auto_ack=False
    )
    channel.start_consuming()


if __name__ == '__main__':
    main()