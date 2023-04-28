from builds import Build
import json
from collections import namedtuple 
import discord
import discord.ext
from typing import List

class CompBuildRole():
    build_name: str
    allowed_discord_role: int

    def __init__(self, build_name: str, allowed_discord_role: int):
        self.allowed_discord_role = allowed_discord_role
        self.build_name = build_name

    def get_build_name(self):
        return self.build_name

class Comp():
    name: str
    description: str
    builds = []

    def __init__(self, name: str, description: str, builds = []):
        self.name = name
        self.description = description
        self.builds = builds

    def addBuild(self, buildName: str, role: discord.Role):
        if role == None:
            self.builds.append(CompBuildRole(buildName, None))
        else:
            self.builds.append(CompBuildRole(buildName, role.id))

    def removeBuild(self, buildName: str):
        for x in self.builds:
            if x["build_name"] == buildName:
                itemToRemove = x 
                break

        if itemToRemove != None:
            self.builds.remove(itemToRemove)

    def as_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def create_discord_embed(self, int: discord.Interaction):
        comp_description = self.description + '\n\n'
        for x in self.builds:
            
            comp_description += x['build_name'] + '\t <@&' + str(x['allowed_discord_role']) + '>\n'


        embed_build = discord.Embed(title=self.name, color=discord.Color.random(), description=comp_description)
        return embed_build

def loadFromJson(compJson: str):
    return Comp(**json.loads(compJson))