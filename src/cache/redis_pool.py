import json

import redis

from src.config import get_configs

config = get_configs()

POOL = redis.ConnectionPool(
    host=config.redis_addr, port=config.redis_port, password=config.redis_auth, max_connections=100)

conn = redis.Redis(connection_pool=POOL, db=config.redis_db)

COOKIE_KEY = "cookie"


def save_cookie(cookies):
    if isinstance(cookies, str) or isinstance(cookies, bytes):
        context = cookies
    elif isinstance(cookies, dict):
        context = json.dumps(cookies, ensure_ascii=False)
    else:
        return

    conn.setex(COOKIE_KEY, context, 3600)


def load_cookie():
    result = conn.get(COOKIE_KEY)
    if result:
        return result.decode()
    else:
        return None


if __name__ == '__main__':
    print(load_cookie())
