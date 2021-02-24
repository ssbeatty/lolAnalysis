import os

import yaml


class Config:
    qq = 0
    password = ""
    redis_addr = ""
    redis_port = 6379
    redis_auth = ""
    redis_db = 1

    def __str__(self):
        return "<config qq: {}>".format(self.qq)


def get_configs() -> Config:
    config_obj = Config()
    yaml_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "config.yaml")
    if not os.path.exists(yaml_path):
        raise FileExistsError("config.yaml not exists, please copy from config.yaml.example")
    with open(yaml_path, "rb") as fd:
        conf = yaml.load(fd, Loader=yaml.FullLoader)
        config_obj.qq = int(conf.get("qq"))
        config_obj.password = str(conf.get("password"))
        redis_conf = conf.get("redis")
        config_obj.redis_addr = redis_conf.get("addr")
        config_obj.redis_port = redis_conf.get("port")
        config_obj.redis_auth = redis_conf.get("auth")
        config_obj.redis_db = redis_conf.get("db")
    return config_obj
