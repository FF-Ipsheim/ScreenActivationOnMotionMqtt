import logging
import threading
import time
from enum import Enum

from screen_activator import ScreenActivator

LOGGER = logging.getLogger(__name__)


class TimerStatus(Enum):
    STARTED = 1
    STOPPED = 2


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
        self.current_status = TimerStatus.STOPPED

    def create_new_timer(self):
        self.timer = threading.Timer(self.interval, self.__finished_timer)

    def start(self):
        with self.lock:
            if self.current_status == TimerStatus.STARTED:
                return

            LOGGER.debug('Start shutdown timer')

            self.timer.start()
            self.current_status = TimerStatus.STARTED

    def stop(self):
        with self.lock:
            if self.current_status == TimerStatus.STOPPED:
                return

            LOGGER.debug('Stop shutdown timer')
            self.timer.cancel()
            self.create_new_timer()
            self.current_status = TimerStatus.STOPPED

    def restart(self):
        LOGGER.debug('Restart shutdown timer')

        self.stop()
        time.sleep(5)
        self.start()

    def __finished_timer(self):
        LOGGER.info('=> Motion detection timed out')
        self.screenActivator.deactivate()
        self.stop()
