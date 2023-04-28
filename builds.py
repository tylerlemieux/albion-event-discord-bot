import json
import discord
import discord.ext
from lookup import weapons
from collections import namedtuple 

class Build():
    name: str
    weapon: str
    head: str
    body: str
    feet: str
    offhand: str

    def __init__(self, name: str, weapon: str, head: str, body: str, feet: str, offhand: str):
        self.name = name
        self.weapon = weapon
        self.head = head
        self.body = body
        self.feet = feet
        self.offhand = offhand

    def as_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def create_discord_embed(self):
        build_description = self.weapon.title() + '\n' + self.head.title() + '\n' + self.body.title() + '\n' + self.feet.title()
        if(self.offhand != None):
            build_description += '\n' + self.offhand.title()  

        embed_build = discord.Embed(title=self.name, url=weapons[self.weapon], color=discord.Color.random(), description=build_description)
        embed_build.set_image(url=weapons[self.weapon])
        return embed_build
        

class build_encoder():
    def default(self, o: Build):
        return o.__dict__

def buildEncoder(build_dict):
    return namedtuple('X', build_dict.keys())(*build_dict.values())

def loadFromJson(buildJson: str):
    return Build(**json.loads(buildJson))