import logging
import subprocess
from kiosk.MonitorActivation.screen_processor import ScreenProcessor

LOGGER = logging.getLogger(__name__)


class VcgencmdProcessor(ScreenProcessor):

    @staticmethod
    def power_on_screen():

        LOGGER.info('power on screen with vcgencmd')

        # send CEC signal to turn screen on
        subprocess.call('vcgencmd display_power 1', shell=True)

    @staticmethod
    def standby_screen():

        LOGGER.info('power off screen with vcgencmd')

        # send CEC signal to turn screen off
        subprocess.call('vcgencmd display_power 0', shell=True)
