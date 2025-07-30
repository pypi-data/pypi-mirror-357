from confclasses.exceptions import ConfclassesAttributeError

# Becareful accessing the __config__ attribute directly, it may not be loaded
_LOADED = "__loaded__"
_CONFIG = "__config__"

class ConfclassWrapper:
    def __init__(self, cls):
        setattr(self, _LOADED, False)
        setattr(self, _CONFIG, None)

    def __getattr__(self, name):
        if name.startswith("__"):
            return object.__getattribute__(self, name)
        
        if self.loaded:
            return getattr(object.__getattribute__(self, _CONFIG), name)
        
        raise ConfclassesAttributeError(f"Attempted to access attribute {name} before configuration was loaded")