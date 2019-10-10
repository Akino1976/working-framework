

class ContextError(Exception):
    pass


class ContextStore(dict):
    def __init__(self, name):
        self.name = name

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            raise ContextError(f"'{key}' not found in {self.name} context")


class FantesticContext:
    def __init__(self):
        self.identifiers = ContextStore('identifier')
        self.database = ContextStore('database')
