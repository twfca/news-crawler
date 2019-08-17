import logging
import random
import time
from functools import wraps
from typing import Callable, Union


def throttle(seconds: Union[int, float]):
    def dec(fn: Callable):
        last_running = 0

        @wraps(fn)
        def wrapper(*args, **kwargs):
            nonlocal last_running
            nonlocal seconds
            seconds = random.uniform(seconds/2, seconds + 5)
            if time.time() - last_running > seconds:
                last_running = time.time()
                return fn(*args, **kwargs)

            while time.time() - last_running <= seconds:
                logging.info(
                    f'{fn.__name__} will be called after {seconds-time.time()+last_running:.0f} second'
                )
                time.sleep(1)

            last_running = time.time()
            return fn(*args, **kwargs)
        return wrapper
    return dec
