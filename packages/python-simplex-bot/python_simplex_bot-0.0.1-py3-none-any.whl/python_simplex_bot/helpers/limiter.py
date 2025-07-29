"""
Limiter class to limit the number of messages sent by a user
"""

class Limiter:
    def __init__(self, limit: int, interval: int):
        self.limit = limit
        self.interval = interval