import logging
from gpiozero import MotionSensor

from screen_activator import ScreenActivator
from motion_detect_timer import MotionDetectionTimer

LOGGER = logging.getLogger(__name__)


class PirWatcher:

    GPIO_PIN = 23  # see https://www.elektronik-kompendium.de/sites/raspberry-pi/1907101.htm

    def __init__(self, _motion_detect_timer: MotionDetectionTimer, _screen_activator: ScreenActivator):
        self.sensor = MotionSensor(self.GPIO_PIN)

        self.screen_activator = _screen_activator
        self.motion_detect_timer = _motion_detect_timer

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

    def start(self):
        """
        Starts motion tracking
        """

        LOGGER.info('Start motion detection ...')

        self.sensor.when_motion = self._motion_detected
        self.sensor.when_no_motion = self._no_motion_detected

    def stop(self):
        LOGGER.info('Stop motion detection ...')

        self.sensor.when_motion = None
        self.sensor.when_no_motion = None

        self.motion_detect_timer.stop()

        self.cleanup()

    def cleanup(self):
        self.sensor.close()
