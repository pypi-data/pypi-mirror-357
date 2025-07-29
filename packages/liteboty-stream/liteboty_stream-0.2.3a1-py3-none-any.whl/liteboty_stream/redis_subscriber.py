import redis
from PIL import Image
from io import BytesIO

from liteboty.core.message import Message


class RedisSubscriber:
    def __init__(self, broker, channel, decode_format):
        self.broker = broker
        self.channel = channel
        self.decode_format = decode_format
        self.client = redis.Redis(host=broker.split(":")[0], port=int(broker.split(":")[1]))
        self.pubsub = self.client.pubsub()
        self.pubsub.subscribe(self.channel)

    def listen(self):
        for raw_message in self.pubsub.listen():
            if raw_message['type'] == 'message':
                message = Message.decode(raw_message['data'])
                image_data = message.data
                img = Image.open(BytesIO(image_data))
                img = img.convert(self.decode_format)  # Decode to the specified format
                yield img
