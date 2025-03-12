from queue import Queue


class SharedRsc:
    data = {}

    def __init__(self):
        pass

    @classmethod
    def set(cls, key: str, val):
        cls.data[key] = val    
    
    @classmethod
    def get(cls, key):
        return cls.data.get(key, None)

sharedResources = SharedRsc()
