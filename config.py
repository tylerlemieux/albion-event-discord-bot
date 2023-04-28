from typing import List
import json

class Configuration():
    allowed_roles: List[int]
    event_channel: int

    def __init__(self, allowed_roles: List[int] = [], event_channel: int = None):
        self.allowed_roles = allowed_roles
        self.event_channel = event_channel
    
    def add_role(self, role: int):
        self.allowed_roles.append(role)

    def remove_role(self, role: int):
        self.allowed_roles.remove(role);

    def as_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

def loadFromJson(configJson: str):
    return Configuration(**json.loads(configJson))