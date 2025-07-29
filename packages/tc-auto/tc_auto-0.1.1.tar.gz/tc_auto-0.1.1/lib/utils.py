import time


def retry_with_conditions(max_retries, interval_time):
    """
    :param max_retries:
    :param interval_time:
    :return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    is_retry = False
                    for retry_message in []:
                        if retry_message in str(e):
                            is_retry = True
                            retries += 1
                            time.sleep(interval_time)
                            break
                    if not is_retry:
                        raise e

        return wrapper
