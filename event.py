import json
import discord
import discord.ext
from comps import Comp
import datetime
from typing import List

class EventPlayer():
    user: int
    build: str
    allowed_role: int

    def __init__(self, build: str, allowed_role:int, user: int = None) -> None:
        self.build = build
        self.user = user
        self.allowed_role = allowed_role


class Event():
    name: str
    description: str
    utcTime: str
    fill_players: List[int]
    comp_name:str
    players: List[EventPlayer]
    maintain_message_id: int

    def __init__(self, name: str, description: str, utcTime: str, fill_players = [], comp_name: str = None, players = [], maintain_message_id: int = None):
        self.name = name
        self.description = description
        get_event_as_date(utcTime)
        self.utcTime = utcTime
        self.fill_players = fill_players
        self.comp_name = comp_name
        self.players = players
        self.maintain_message_id = maintain_message_id
 
    def set_comp(self, comp: Comp, int: discord.Interaction):
        self.comp_name = comp.name
        for build in comp.builds:
            event_player = EventPlayer(build['build_name'], build['allowed_discord_role'])
            self.players.append(event_player)

    
    def set_message_id(self, message_id: int):
        self.maintain_message_id = message_id

    def join_event(self, int: discord.Interaction, build_name: str = None) -> str:
        if build_name == None:
            # User is joining as a fill
            if not (int.user.id in self.fill_players):
                self.fill_players.append(int.user.id)
                return "Successfully joined event as a filler"
            else:
                return 'You are already a part of this event'
        else:
            for build in self.players:
                if build['build'] == build_name and build['user'] == None:
                    # Check user's rank
                    if build['allowed_role'] == None or int.user.get_role(build['allowed_role']) != None:
                        # No role is required or the user has the role
                        build['user'] = int.user.id
                        return 'Successfully joined as ' + build_name
                    else:
                        return 'You lack the required rank to sign up for this role'
            
            # If we got here, they were unable to join 
            return 'Failed to join the event'

    def as_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def create_discord_embed(self, int: discord.Interaction):
        event_description = get_event_as_date(self.utcTime).strftime("%m/%d/%Y, %H:%M") + '\n'
        event_description += self.description + '\n\n Signed Up:\n'

        for x in self.players:
            event_description += x['build']
            
            if x['user'] != None:
                event_description += '\t' + '<@' + str(x['user']) + '>'
            elif x['allowed_role'] != None:
                event_description += '\t <@&' + str(x['allowed_role']) + '>'

            event_description += '\n'

        event_description += '\nFillers:\n'
        for x in self.fill_players:
            event_description += '<@' + str(x) + '>\n'

        embed_build = discord.Embed(title=self.name, color=discord.Color.random(), description=event_description)
        return embed_build

def get_event_as_date(datetimeString: str):
    return datetime.datetime.fromisoformat(datetimeString) 

def loadFromJson(eventJson: str):
    return Event(**json.loads(eventJson))