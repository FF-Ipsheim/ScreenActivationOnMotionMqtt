import logging
import os
import time
import socket

import paho.mqtt.client as paho
from paho import mqtt

from screen_activator import ScreenActivator
from motion_detect_timer import MotionDetectionTimer

LOGGER = logging.getLogger(__name__)

class PirWatcher:

    def __init__(self, _motion_detect_timer: MotionDetectionTimer, _screen_activator: ScreenActivator):
        self.screen_activator = _screen_activator
        self.motion_detect_timer = _motion_detect_timer
        self._initialize_settings()
        self.client = self._connect_mqtt()

    def _initialize_settings(self):
        self.BROKER = os.getenv('BROKER')
        self.PORT = int(os.getenv('PORT', 8883))
        self.USE_TLS = bool(os.getenv('USE_TLS', True))
        self.TOPIC = os.getenv('TOPIC')
        self.LAST_WILL_TOPIC = os.getenv('LAST_WILL_TOPIC')
        self.USE_LAST_WILL = bool(os.getenv('USE_LAST_WILL', True))
        # generate client ID with pub prefix randomly
        self.CLIENT_ID = f'{os.getenv("CLIENT_ID_PREFIX", "pir-watcher")}-{socket.gethostname()}-{time.time_ns()}'
        self.USE_AUTHENTICATION = bool(os.getenv('USE_AUTHENTICATION', True))
        self.USERNAME = os.getenv('USERNAME', '')
        self.PASSWORD = os.getenv('PASSWORD', '')

        self.FIRST_RECONNECT_DELAY = int(os.getenv('FIRST_RECONNECT_DELAY', 1))
        self.RECONNECT_RATE = int(os.getenv('RECONNECT_RATE', 2))
        self.USE_RECONNECT_FOREVER = bool(os.getenv('USE_RECONNECT_FOREVER', True))
        self.MAX_RECONNECT_COUNT = int(os.getenv('MAX_RECONNECT_COUNT', 12))
        self.MAX_RECONNECT_DELAY = int(os.getenv('MAX_RECONNECT_DELAY', 60))
        self.QOS = int(os.getenv('QOS', 1))

        self._dump_connection_settings()

    def _dump_connection_settings(self):
        msg = f'''
==============
MQTT settings:
==============

SERVER:
    BROKER:                 {self.BROKER}
    PORT:                   {self.PORT}

AUTHENTICATION:
    USERNAME:               {self.USERNAME}
    PASSWORD:               {self.PASSWORD}

SWITCHES:
    USE_TLS:                {self.USE_TLS}
    USE_LAST_WILL:          {self.USE_LAST_WILL}
    USE_AUTHENTICATION:     {self.USE_AUTHENTICATION}
    USE_RECONNECT_FOREVER:  {self.USE_RECONNECT_FOREVER}

TOPICS:
    TOPIC:                  {self.TOPIC}
    LAST_WILL_TOPIC:        {self.LAST_WILL_TOPIC}

CONNECTION PARAMETER:
    CLIENT_ID:              {self.CLIENT_ID}
    FIRST_RECONNECT_DELAY:  {self.FIRST_RECONNECT_DELAY}
    RECONNECT_RATE:         {self.RECONNECT_RATE}
    MAX_RECONNECT_COUNT:    {self.MAX_RECONNECT_COUNT}
    MAX_RECONNECT_DELAY:    {self.MAX_RECONNECT_DELAY}
    QOS:                    {self.QOS}        
        
'''
        LOGGER.info(msg)

    # Upon connection, Paho calls the on_connect() function, which can be defined as needed.
    # It is the callback for when the client receives a CONNACK response from the server.
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0 and client.is_connected():
            LOGGER.info(f'Connected to MQTT Broker with status: {rc}')
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe(self.TOPIC, qos=self.QOS, options=None, properties=None)
            LOGGER.info(f'Subscribed to topic `{self.TOPIC}`')
        else:
            LOGGER.info(f'Failed to connect, return code {rc}')

    def _on_disconnect(self, client, userdata, rc, properties=None):
        LOGGER.info('Disconnected with result code: %s', rc)
        reconnect_count, reconnect_delay = 0, self.FIRST_RECONNECT_DELAY

        # should reconnect forever or give it only n-retries
        reconnect_test = self._reconnect_forever
        if not self.USE_RECONNECT_FOREVER:
            reconnect_test = self._reconnect_give_a_next_try

        while reconnect_test(reconnect_count):
            LOGGER.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                LOGGER.info("Reconnected successfully!")
                return
            except Exception as err:
                LOGGER.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= self.RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, self.MAX_RECONNECT_DELAY)
            reconnect_count += 1

        if not self.USE_RECONNECT_FOREVER:
            LOGGER.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        LOGGER.info("Subscribed: " + str(mid) + " " + str(granted_qos))

    # The callback for when a PUBLISH message is received from the server.
    def _on_message(self, client, userdata, msg):
        LOGGER.info(f'Received `{msg.payload.decode()}` from topic `{msg.topic}`')

        # data = json.loads(msg.payload.decode('utf-8'))
        # log.info(data)
        # return await process(data=data)

        self._motion_detected()

    def _connect_mqtt(self):
        # Creates an instance of the MQTT client
        client = paho.Client(client_id=self.CLIENT_ID, userdata=None, protocol=paho.MQTTv5)

        # enable TLS for secure connection
        if self.USE_TLS:
            client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

        # Logs in if there is an existing user defined on the broker side
        if self.USE_AUTHENTICATION:
            client.username_pw_set(self.USERNAME, self.PASSWORD)
        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_subscribe = self._on_subscribe
        client.on_message = self._on_message

        client.will_set('pir/last-will', self.CLIENT_ID, 0, False)

        LOGGER.info(f'Connect to broker {self.BROKER} with port {self.PORT}')

        # Broker address and port defined on broker side, keep-alive of choice
        client.connect_async(self.BROKER, self.PORT, keepalive=120)

        return client

    def _motion_detected(self):
        """
        This method gets called when a motion is detected.
        """
        
        LOGGER.info('motion detected')

        self.motion_detect_timer.stop()
        self.screen_activator.activate()

    def _no_motion_detected(self):
        """
        This method gets called when the sensor changes state from active to inactive.
        """

        LOGGER.info('no motion detected')

        self.motion_detect_timer.restart()

    def _reconnect_forever(self, reconnect_count):
        return True

    def _reconnect_give_a_next_try(self, reconnect_count):
        return reconnect_count < self.MAX_RECONNECT_COUNT

    def start(self):
        """
        Starts motion tracking
        """

        LOGGER.info('Start motion detection ...')
        self.client.loop_forever()

    def stop(self):
        LOGGER.info('Stop motion detection ...')

        self.client.loop_stop()

        self.motion_detect_timer.stop()
