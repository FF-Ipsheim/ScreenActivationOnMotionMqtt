#!/usr/bin/env python

import argparse
import logging
from logging.handlers import SysLogHandler
import sys
from signal import pause

from motion_detect_timer import MotionDetectionTimer
from pir_watcher import PirWatcher
from screen_activator import ScreenActivator

LOG_FORMAT = '%(asctime)s %(levelname)s %(module)s %(lineno)d: %(message)s'
LOGGER = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Activates the screen on monition an puts it in standby after a given '
                                             'delay of no motion')
parser.add_argument('-t', '--processor_type', dest='processor_type', action='store', default='cec_client', type=str,
                    choices=['cec_client', 'vcgencmd'],
                    help='sets the processor type to talk with the screen. '
                         'Possible values: cec_client [default], vcgencmd')
parser.add_argument('-i', '--no_motion_interval', dest='no_motion_interval', action='store', default=600, type=int,
                    help='sets the interval to shutdown the screen after NO motion is detected. '
                         'The value is in seconds. The default is 600 (= 10 minutes).')


def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT,
                        handlers=[logging.FileHandler('ScreenActivationOnMotion.log', mode='w'),
                                  logging.StreamHandler(sys.stdout),
                                  logging.handlers.SysLogHandler()])
    args = parser.parse_args()

    LOGGER.info('Start screen activation on motion ...')

    screen_activator = ScreenActivator(args.processor_type)
    timer = MotionDetectionTimer(screen_activator, args.no_motion_interval)
    pir_watcher = PirWatcher(timer, screen_activator)

    try:
        pir_watcher.start()
        pause()

    except KeyboardInterrupt:
        pir_watcher.stop()
        timer.stop()

    LOGGER.info('Terminate')


if __name__ == '__main__':
    main()
