import json


class RabbitMqHandler():
    def __init__(self, channel, config):
        self._channel = channel
        self._config = config

    def publish_message(self, message):
        self._channel.basic_publish(
            exchange='',
            routing_key=self._config.rabbitmq_queue,
            body=json.dumps(message),
        )
