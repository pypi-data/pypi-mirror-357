import json
import os
from typing import List

import pika
from whitson_tool_helper.logger import LOGGER
from whitson_tool_helper.messaging.helper import check_environment_variables


def get_rabbitmq_params():
    check_environment_variables(
        [
            "RABBITMQ_USER",
            "RABBITMQ_PASSWORD",
            "RABBITMQ_HOST",
            "RABBITMQ_PORT",
        ],
    )
    credentials = pika.PlainCredentials(
        os.environ["RABBITMQ_USER"], os.environ["RABBITMQ_PASSWORD"]
    )
    return pika.ConnectionParameters(
        host=os.environ["RABBITMQ_HOST"],
        port=os.environ["RABBITMQ_PORT"],
        credentials=credentials,
        heartbeat=1200,
    )


class RabbitMQConsumer:
    def __init__(self, process_function, service: str = "listener"):
        self.process_function = process_function
        self.well_id = None
        self.model = None
        self.delivery_tag = None
        self.service = service
        check_environment_variables(["MESSAGING_SUBSCRIPTION"])

    def _callback(self, ch, method, properties, body):
        if not body or body.decode("utf-8") == "":
            ch.basic_ack(delivery_tag=method.delivery_tag)
            LOGGER.info("Recieved faulty message")
            LOGGER.info(f"Listening to {method.routing_key}...")
            return

        msg = json.loads(body.decode("utf-8"))
        self.well_id = msg["data"].get("well_id") or "Unkown"
        self.model = msg["data"].get("model") or "Unkown"
        self.delivery_tag = method.delivery_tag
        self.process_function(data=msg["data"], meta_data=msg["meta_data"])
        LOGGER.info("  ---  SUCCESS  ---  ")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        LOGGER.info(f"Listening to {method.routing_key} ...")

    def _initialize_connection_and_channel(self):
        parameters = get_rabbitmq_params()
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        subscription = os.getenv("MESSAGING_SUBSCRIPTION")
        if self.service == "uploader":
            subscription = os.environ["UPLOADER_SUBSCRIPTION"]
        LOGGER.info(f"Listening to {subscription}...")
        self.channel.queue_declare(
            queue=subscription,
            durable=True,
            arguments={"x-max-priority": 100, "x-queue-type": "classic"},
        )
        exchange = "engines"
        if subscription.endswith("-calculated") or subscription.endswith("-upload"):
            exchange = "clients"

        self.channel.queue_bind(
            queue=subscription, exchange=exchange, routing_key=subscription
        )
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=subscription, on_message_callback=self._callback
        )

    def ack_and_close_connection(self):
        LOGGER.critical(f"Destroyed calc {self.model} for well {self.well_id}")
        self.channel.basic_ack(delivery_tag=self.delivery_tag)
        self.channel.stop_consuming()

    def work(self):
        self._initialize_connection_and_channel()
        self.channel.start_consuming()


class RabbitMQPublisher:
    def __init__(self, exchange):
        self.parameters = get_rabbitmq_params()
        self.exchange = exchange

    def publish(
        self, topic: str, payload: dict, meta_data: dict = {}, priority: int = 50
    ):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()

        message = {"data": payload, "meta_data": meta_data}

        channel.basic_publish(
            exchange=self.exchange,
            routing_key=topic,
            body=json.dumps(message).encode("utf-8"),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                priority=priority,
            ),
        )

        connection.close()

    def publish_many(self, topic, payloads: List[dict], priority: int = 50):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()

        for message in payloads:
            channel.basic_publish(
                exchange=self.exchange,
                routing_key=topic,
                body=json.dumps(message).encode("utf-8"),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                    priority=priority,
                ),
            )

        connection.close()


class RabbitMQMover:
    def __init__(self):
        self.parameters = get_rabbitmq_params()

    def move(self, number_of_messages: int, source: str, destination: str):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()

        for _ in range(number_of_messages):
            method_frame, header_frame, body = channel.basic_get(
                queue=source, auto_ack=False
            )
            if method_frame:
                channel.basic_publish(
                    exchange="engines",
                    routing_key=destination,
                    body=body,
                    properties=pika.BasicProperties(
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                        priority=100,
                    ),
                )
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            else:
                LOGGER.warning("No more messages to move")
                break

        connection.close()
