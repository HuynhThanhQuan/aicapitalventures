import yaml
import os


class TCBSSpecification(dict):
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set(cls, config):
        dir = os.path.dirname(__file__)
        fp = os.path.join(dir, 'config.yaml')
        with open(fp, 'w') as f:
            yaml.dump(config, f)

    def load_spec(cls):
        dir = os.path.dirname(__file__)
        fp = os.path.join(dir, 'config.yaml')
        data = yaml.safe_load(open(fp, 'r'))
        return data


SPECIFICATION = TCBSSpecification()
