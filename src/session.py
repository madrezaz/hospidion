from src.models import Classification


class Session:
    def __init__(self, type: str, pid: str, section: str, username: str, manage_role: str, role: str, asl: Classification, rsl: Classification, wsl: Classification):
        self.username = username
        self.asl = asl
        self.rsl = rsl
        self.wsl = wsl
        self.type = type
        self.pid = pid
        self.section = section
        self.manage_role = manage_role
        self.role = role
