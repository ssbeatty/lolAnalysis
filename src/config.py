import os

import yaml


class Config:
    qq = 0
    password = ""

    def __str__(self):
        return "<config qq: {}>".format(self.qq)


def get_configs():
    config_obj = Config()
    yaml_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "config.yaml")
    if not os.path.exists(yaml_path):
        raise FileExistsError("config.yaml not exists, please copy from config.yaml.example")
    with open(yaml_path, "rb") as fd:
        conf = yaml.load(fd, Loader=yaml.FullLoader)
        config_obj.qq = int(conf.get("qq"))
        config_obj.password = str(conf.get("password"))
    return config_obj
