from pydantic import BaseModel


class User(BaseModel):
    """
    User class to represent a user
    """
    id: int
    username: str

    def __str__(self):
        return f'@{self.username}'

class Group(BaseModel):
    """
    Group class to represent a group
    """
    group: str

    def __str__(self):
        return f'#{self.group}'

class Peer(BaseModel):
    """
    Peer class to represent a user or a group
    """
    user: User|None = None
    group: Group|None = None

    def __str__(self):
        if self.user:
            return str(self.user)
        else:
            return str(self.group)
