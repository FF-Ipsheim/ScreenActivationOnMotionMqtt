import logging
import threading

from screen_activator import ScreenActivator

LOGGER = logging.getLogger(__name__)


class MotionDetectionTimer:
    interval = 60

    def __init__(self, screen_activator: ScreenActivator, no_motion_interval: int = 10 * 60) -> None:
        """
        Initializes the motion detection timer
        :param screen_activator: The screen activator
        :param no_motion_interval: The interval no motion should be detected to call screen_activator.deactivate.
               The default is 600.
        """
        self.screenActivator = screen_activator
        self.interval = no_motion_interval
        self.timer = threading.Timer(self.interval, self.__finished_timer)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def restart(self):
        self.stop()
        self.start()

    def __finished_timer(self):
        LOGGER.info('motion detection timed out')
        self.screenActivator.deactivate()
        pass
