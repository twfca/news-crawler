import logging
import pickle
import random
import time
from functools import wraps
from typing import Callable, Union

from pony.orm import Database


def throttle(seconds: Union[int, float]):
    def dec(fn: Callable):
        last_running = 0

        @wraps(fn)
        def wrapper(*args, **kwargs):
            nonlocal last_running

            if time.time() - last_running > seconds:
                last_running = time.time()
                return fn(*args, **kwargs)

            while time.time() - last_running <= seconds:
                logging.info(
                    '%r will be called after %.0f second',
                    fn.__name__,
                    seconds-time.time()+last_running
                )
                time.sleep(1)

            last_running = time.time()
            return fn(*args, **kwargs)
        return wrapper
    return dec

def random_throttle(seconds: Union[int, float]):
    s = random.uniform(seconds/2, seconds + 5)
    return throttle(s)

def cache(fn: Callable):
    memo = {}
    @wraps(fn)
    def wrapper(*args, **kwargs):
        key = pickle.dumps(args) + pickle.dumps(kwargs)

        if key not in memo:
            logging.debug('Caching %r %r %r...',
                fn.__name__,
                args,
                kwargs
            )
            memo[key] = fn(*args, **kwargs)

        return memo[key]
    return wrapper