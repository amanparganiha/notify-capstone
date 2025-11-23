"""
Simple in-memory session and a tiny MemoryBank backed by sqlitedict.
"""
from sqlitedict import SqliteDict

class InMemorySession:
    def __init__(self, session_id="default"):
        self.session_id = session_id
        self.store = {}

    def write(self, key, value):
        self.store[key] = value

    def read(self, key, default=None):
        return self.store.get(key, default)

class MemoryBank:
    def __init__(self, path="memory.sqlite"):
        self.db = SqliteDict(path, autocommit=True)

    def set(self, key, value):
        self.db[key] = value

    def get(self, key, default=None):
        return self.db.get(key, default)
