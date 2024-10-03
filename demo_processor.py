import logging

from screen_processor import ScreenProcessor


LOGGER = logging.getLogger(__name__)


class DemoProcessor(ScreenProcessor):

    @staticmethod
    def power_on_screen():

        LOGGER.info('power on screen with demo-client')

    @staticmethod
    def standby_screen():

        LOGGER.info('power off screen with demo-client')
