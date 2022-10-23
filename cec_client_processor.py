import logging
import subprocess

from screen_processor import ScreenProcessor


LOGGER = logging.getLogger(__name__)


class CecClientProcessor(ScreenProcessor):

    @staticmethod
    def power_on_screen():

        LOGGER.info('power on screen with cec-client')

        # send CEC signal to turn screen on
        subprocess.call('echo "on 0" | cec-client -s -d 1', shell=True)

    @staticmethod
    def standby_screen():

        LOGGER.info('power off screen with cec-client')

        # send CEC signal to turn screen off
        subprocess.call('echo "standby 0" | cec-client -s -d 1', shell=True)
