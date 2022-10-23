import logging
import threading
import time

from screen_activator import ScreenActivator

LOGGER = logging.getLogger(__name__)


class MotionDetectionTimer:

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
        self.lock = threading.Lock()

    def start(self):
        self.lock.acquire()
        self.timer.start()
        self.lock.release()

    def stop(self):
        self.lock.acquire()
        self.timer.cancel()
        self.lock.release()

    def restart(self):
        self.stop()
        time.sleep(5)
        self.start()

    def __finished_timer(self):
        LOGGER.info('motion detection timed out')
        self.screenActivator.deactivate()
        pass
