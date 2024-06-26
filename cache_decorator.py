import json
from datetime import timedelta
from functools import wraps
from typing import Callable, Optional

from db import db


def key_db_cache(ttl: Optional[timedelta] = None) -> Callable:
    def wrapper(func: Callable):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            key = f'{func.__name__}{args}'

            if db.exists(key):
                response_from_cache = db.get(key)
                return json.loads(response_from_cache)

            response = func(*args, **kwargs)

            db.set(key, json.dumps(response, default=lambda obj: obj.dict()), ex=ttl)

            return response

        return _wrapper

    return wrapper
