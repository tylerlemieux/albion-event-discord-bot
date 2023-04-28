# This is new in the discord.py 2.0 update

# imports
import discord
import discord.ext
from typing import Literal, List
from lookup import head_items, body_items, feet_items, weapons, offhands, weapons_literal, body_items_literal, head_items_literal, feet_items_literal, offhands_literal
from builds import Build, loadFromJson
from config import Configuration
import config
import comps
from comps import Comp
import os
from event import Event
import event
import threading
from time import sleep
import asyncio

# setting up the bot
intents = discord.Intents.all() 
# if you don't want all intents you can do discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

# sync the slash command to your server
@client.event
async def on_ready():
    await tree.sync()
    # print "ready" in the console when the bot is ready to work
    print("ready")

@tree.command(name="list-items", description="list all items of a type")
async def slash_command(int: discord.Interaction, item_type: Literal['head', 'body', 'feet', 'weapon', 'offhand']):   
    if(item_type == 'head'):
        await int.response.send_message('\n'.join(head_items.keys()))
    elif(item_type == 'body'):
        await int.response.send_message('\n'.join(body_items.keys()))
    elif(item_type == 'weapon'):
        await int.response.send_message('\n'.join(weapons.keys()))
    elif(item_type == 'offhand'):
        await int.response.send_message('\n'.join(offhands.keys()))        
    elif(item_type == 'feet'):
        await int.response.send_message('\n'.join(feet_items.keys()))

@tree.command(name='createbuild', description="Create a new build")
async def createbuild(int: discord.Interaction, name: str, weapon: str, head: str, body: str, feet: str, offhand: Literal[offhands_literal]=None):
    # NOTE we cannot use the options literal for anything with more than 25 options
    if not (weapon in weapons_literal):
        await int.response.send_message('Invalid weapon', delete_after=5)
        return

    if not (offhand in offhands_literal):
        await int.response.send_message('Invalid offhand', delete_after=5)
        return

    if not (body in body_items_literal):
        await int.response.send_message('Invalid body', delete_after=5)
        return

    if not (head in head_items_literal):
        await int.response.send_message('Invalid head', delete_after=5)
        return

    if not (feet in feet_items_literal):
        await int.response.send_message('Invalid feet', delete_after=5)
        return
    
    new_build = Build(name, weapon, head, body, feet, offhand)
    write_build(int.guild_id, new_build)
    await int.response.send_message(embed=new_build.create_discord_embed())

@tree.command(name='getbuild', description="Lookup an existing build")
async def getbuild(int: discord.Interaction, name: str):
    loaded_build = load_build(int.guild_id, name)
    await int.response.send_message(embed=loaded_build.create_discord_embed())

@tree.command(name='createcomp', description='Create a comp for an activity as a list of builds')
async def createcomp(int: discord.Interaction, name: str, description: str):
    if not create_is_allowed(int) and not int.user.guild_permissions.administrator:
        await int.response.send_message("You are not in an allowed role to create, please contact a server admin")
        return

    new_comp = Comp(name, description, [])
    write_comp(int.guild_id, new_comp)
    await int.response.send_message(embed=new_comp.create_discord_embed(int))

@tree.command(name='removecompbuild', description='Gives information about a created comp')
async def removecompbuild(int: discord.Interaction, name: str, build_to_remove: str):
    if not create_is_allowed(int) and not int.user.guild_permissions.administrator:
        await int.response.send_message("You are not in an allowed role to create, please contact a server admin")
        return
        
    loaded_comp = load_comp(int.guild_id, name)
    loaded_comp.removeBuild(build_to_remove)
    write_comp(int.guild_id, loaded_comp)
    await int.response.send_message(embed=loaded_comp.create_discord_embed(int))

@tree.command(name='addcompbuild', description='Gives information about a created comp')
async def addcompbuild(int: discord.Interaction, name: str, build_to_add: str, allowed_role: discord.Role = None):
    if not create_is_allowed(int) and not int.user.guild_permissions.administrator:
        await int.response.send_message("You are not in an allowed role to create, please contact a server admin")
        return
        
    loaded_comp = load_comp(int.guild_id, name)
    loaded_comp.addBuild(build_to_add, allowed_role)
    write_comp(int.guild_id, loaded_comp)
    loaded_comp = load_comp(int.guild_id, name)
    await int.response.send_message(embed=loaded_comp.create_discord_embed(int))

@tree.command(name='getcomp', description='Gives information about a created comp')
async def getcomp(int: discord.Interaction, name: str):
    loaded_comp = load_comp(int.guild_id, name)
    await int.response.send_message(embed=loaded_comp.create_discord_embed(int))

@tree.command(name='createevent', description='Creates a new event.  Expects date in ISO8601 Format ex. 2020-02-08 09Z The Z specifies UTC timezone')
async def createevent(int: discord.Interaction, name: str, description: str, event_time: str, comp_name: str):
    if not create_is_allowed(int) and not int.user.guild_permissions.administrator:
        await int.response.send_message("You are not in an allowed role to create, please contact a server admin")
        return

    new_event = Event(name, description, event_time)
    comp = load_comp(int.guild_id, comp_name)
    new_event.set_comp(comp, int)
    write_event(int.guild_id, new_event)
    new_event = load_event(int.guild_id, name)

    c = load_config(int.guild_id)

    message = await tree.client.get_channel(c.event_channel).send(embed=new_event.create_discord_embed(int))
    new_event.set_message_id(message.id)
    write_event(int.guild_id, new_event)
    await int.response.send_message('Successfully created the event', delete_after=5)

@tree.command(name='getevent', description='Display an event information, not really needed, main message will be maintained')
async def getevent(int: discord.Interaction, name: str):
    loaded_event = load_event(int.guild_id, name)
    await int.response.send_message(embed=loaded_event.create_discord_embed(int))
    
@tree.command(name='joinevent', description='Join an event')
async def joinevent(int: discord.Interaction, name: str, build: str = None):
    loaded_event = load_event(int.guild_id, name)
    response = loaded_event.join_event(int, build)
    write_event(int.guild_id, loaded_event) 

    c = load_config(int.guild_id)
    message = await tree.client.get_channel(c.event_channel).fetch_message(loaded_event.maintain_message_id)
    await message.edit(embed=load_event(int.guild_id, name).create_discord_embed(int))
    await int.response.send_message(response, delete_after=5)

@tree.command(name="configchannel")
async def joinevent(int: discord.Interaction, channel: discord.TextChannel):
    if not int.user.guild_permissions.administrator:
        await int.response.send_message('Only admins can update bot config', delete_after=5)
        return 

    config: Configuration
    if config_exists(int.guild_id):
        config = load_config(int.guild_id)
        config.event_channel = channel.id
    else:
        config = Configuration(event_channel=channel.id)

    write_config(int.guild_id, config)
    await int.response.send_message('Set configured channel', delete_after=5)

@tree.command(name="configaddallowrole")
async def joinevent(int: discord.Interaction, role: discord.Role):
    if not int.user.guild_permissions.administrator:
        await int.response.send_message('Only admins can update bot config', delete_after=5)
        return 
        
    config: Configuration
    if config_exists(int.guild_id):
        config = load_config(int.guild_id)
    else:
        config = Configuration()
    config.add_role(role.id)
    write_config(int.guild_id, config)
    await int.response.send_message('Set configured channel', delete_after=5)

@tree.command(name="configremoveallowrole")
async def joinevent(int: discord.Interaction, role: discord.Role):
    if not int.user.guild_permissions.administrator:
        await int.response.send_message('Only admins can update bot config', delete_after=5)
        return 
        
    config: Configuration
    if config_exists(int.guild_id):
        config = load_config(int.guild_id)
    else:
        config = Configuration()
    config.remove_role(role.id)
    write_config(int.guild_id, config)
    await int.response.send_message('Set configured channel', delete_after=5)


def write_build(guild_id: int, build: Build):
    dir = get_base_data_path(guild_id)
    create_directory_if_not_exist(dir)
    file = open(dir + '/build_' + build.name + ".json", "w")
    file.write(build.as_json())
    file.close()

def load_build(guild_id: int, build_name: str) -> Build:
    file = open(get_base_data_path(guild_id) + '/build_' + build_name + '.json', 'r')
    build_instance = loadFromJson(file.read())
    file.close()
    return build_instance

def write_comp(guild_id: int, comp: Comp):
    dir = get_base_data_path(guild_id)
    create_directory_if_not_exist(dir)
    file = open(dir + '/comp_' + comp.name + ".json", "w")
    file.write(comp.as_json())
    file.close()

def load_comp(guild_id: int, comp_name: str) -> Comp:
    file = open(get_base_data_path(guild_id) + '/comp_' + comp_name + '.json', 'r')
    comp_instance = comps.loadFromJson(file.read())
    file.close()
    return comp_instance

def write_event(guild_id: int, event: Event):
    dir = get_base_data_path(guild_id)
    create_directory_if_not_exist(dir)
    file = open(dir + '/event_' + event.name + ".json", "w")
    file.write(event.as_json())
    file.close()

def load_event(guild_id: int, event_name: str) -> Event:
    file = open(get_base_data_path(guild_id) + '/event_' + event_name + '.json', 'r')
    event_instance = event.loadFromJson(file.read())
    file.close()
    return event_instance

def write_config(guild_id: int, config: Configuration):
    dir = get_base_data_path(guild_id)
    create_directory_if_not_exist(dir)
    file = open(dir + '/config.json', "w")
    file.write(config.as_json())
    file.close()

def load_config(guild_id: int) -> Configuration:
    file = open(get_base_data_path(guild_id) + '/config.json', 'r')
    c = config.loadFromJson(file.read())
    file.close()
    return c

def config_exists(guild_id: int) -> bool:
    return os.path.isfile(get_base_data_path(guild_id) + '/config.json')

def create_directory_if_not_exist(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_base_data_path(guild_id: str) -> str:
    return "data/build/" + str(guild_id)


def build_exists(build_name: str) -> bool:
    return True

def item_exists(item_name: str) -> bool:
    return True

def create_is_allowed(int: discord.Interaction) -> bool:
    config = load_config(int.guild_id)
    for role in config.allowed_roles:
        if int.user.get_role(role) == None:
            continue
        else:
            return True
    
    return False


# TODO validate items when making builds 
# TODO validate builds exist when making comp

client.run('MTA3MjUyODQxNjc3NzE4MzMxNA.GhvN4A.LjvlZnZOVIGwh33X5rbRsUa09Dchl_4A0EYvBI')


