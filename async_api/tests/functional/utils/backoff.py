import time
from functools import wraps

import aioredis
import elasticsearch


def backoff(
    start_sleep_time=0.1,
    factor=2,
    border_sleep_time=10,
    max_repeat=10,
):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    :param start_sleep_time: Начальное время повтора.
    :param factor: Во сколько раз нужно увеличить время ожидания.
    :param border_sleep_time: Граничное время ожидания.
    :param max_repeat: Максимальное количество вызовов декоратора backoff.
    :return func_wrapper: Результат выполнения функции.
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            count = 0
            sleep_time = start_sleep_time
            exp = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except (elasticsearch.TransportError, aioredis.exceptions.ConnectionError):
                    count += 1
                    time.sleep(sleep_time)
                    if sleep_time >= border_sleep_time:
                        sleep_time = border_sleep_time
                    else:
                        sleep_time = start_sleep_time * 2 ** (exp)
                        exp *= factor
                finally:
                    if count > max_repeat:
                        raise RuntimeError('Превышено количество вызовов декоратора backoff')

        return inner

    return func_wrapper
