import logging
import keyboard

LOGGER = logging.getLogger(__name__)


class ScreenActivator:
    
    def __init__(self, processor_type='cec_client'):

        if processor_type == 'cec_client':
            from cec_client_processor import CecClientProcessor
            self.processor = CecClientProcessor()
        elif processor_type == 'vcgencmd':
            from vcgencmd_processor import VcgencmdProcessor
            self.processor = VcgencmdProcessor()
        else:
            raise Exception("Date provided can't be in the past")

        keyboard.add_hotkey("ctrl+alt+o", self.__on_wakeup_by_keyboard)

        self.powered_on = None
        self.activate()

    def __del__(self):
        keyboard.unhook_all()

    def __on_wakeup_by_keyboard(self):
        LOGGER.info('Activate monitor by keyboard hotkey')
        self.powered_on = False  # force activate
        self.activate()

    def activate(self):

        LOGGER.info('activate screen')

        if not self.powered_on:
            self.processor.power_on_screen()
            self.powered_on = True

    def deactivate(self):

        LOGGER.info('deactivate screen')

        if self.powered_on:
            self.processor.standby_screen()
            self.powered_on = False
