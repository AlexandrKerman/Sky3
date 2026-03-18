from functools import wraps


def save_return(filename):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            res = func(*args, *kwargs)
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(str(res))
            return res
        return inner
    return wrapper
