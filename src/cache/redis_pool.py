import redis

from src.config import get_configs

config = get_configs()

POOL = redis.ConnectionPool(
    host=config.redis_addr, port=config.redis_port, password=config.redis_auth, max_connections=100, db=config.redis_db)