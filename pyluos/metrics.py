import json
import time
import logging

import requests

from threading import Thread
from datetime import datetime

logger = logging.getLogger(__name__)


def json_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()


class Publisher(object):
    def __init__(self, robot,
                 url='http://teahupoo.ddns.net/post/robot-state.json',
                 push_period=60):

        def pub_loop():
            while True:
                time.sleep(push_period)

                if not robot.alive:
                    continue

                try:
                    requests.post(
                        url=url,
                        data=json.dumps(robot.state,
                                        default=json_handler),
                        headers={
                            'content-type': 'application/json',
                        }
                    )
                except Exception as e:
                    msg = 'Could not post robot state: {}'.format(str(e))
                    logger.info(msg)

        self._pub = Thread(target=pub_loop)
        self._pub.daemon = True

    def start(self):
        self._pub.start()
