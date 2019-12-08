from src.models import Classification


class Session:
    def __init__(self, username: str, asl: Classification, rsl: Classification, wsl: Classification):
        self.username = username
        self.asl = asl
        self.rsl = rsl
        self.wsl = wsl
