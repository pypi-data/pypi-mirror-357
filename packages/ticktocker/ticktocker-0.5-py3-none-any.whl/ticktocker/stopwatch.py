from functools import wraps

from .utils import _millis, TextStyle


def _print_elapsed_time(start: float, end: float, desc: str):
    _elapsed = f'{end - start:.4f}'
    print(f'{TextStyle.green(desc)}: {TextStyle.bold(_elapsed)} ms')


class stopwatch:
    def __init__(self, desc: str = 'stopwatch'):
        self.desc = desc

    # context manager
    def __enter__(self):
        self.start = _millis()
        return self

    # context manager
    def __exit__(self, *args):
        self.end = _millis()
        _print_elapsed_time(self.start, self.end, self.desc)

    # decorator
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _start = _millis()
            result = func(*args, **kwargs)
            _end = _millis()
            _func_name = func.__name__
            _print_elapsed_time(_start, _end, _func_name)
            return result
        return wrapper
