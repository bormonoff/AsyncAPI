import time
from functools import wraps
from typing import Type

from utils.logger import logger


def backoff(
    exceptions: Type[Exception] | tuple[Type[Exception]] = Exception,
    start_sleep_time: float = 0.1,
    factor: float = 2,
    border_sleep_time: float = 10,
):
    """
    Декоратор для повторного вызова функции при возникновении ошибки.
    После каждого неудачного запуска увеличивается промежуток времени до следующего запуска.
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            try_number = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.error(
                        "Function %s was failed. Try number: %d. Sleep time: %d. Exception:\n%s",
                        func.__name__,
                        try_number,
                        sleep_time,
                        str(e),
                    )
                    time.sleep(sleep_time)
                    if sleep_time < border_sleep_time:
                        sleep_time = sleep_time * factor**try_number
                        if sleep_time > border_sleep_time:
                            sleep_time = border_sleep_time
                    try_number += 1

        return inner

    return func_wrapper
