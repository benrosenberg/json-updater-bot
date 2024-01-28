# -*- coding: utf-8 -*-

import discord
from discord import Intents
import json

with open('token.json', 'r') as f:
    token_dict = json.loads(f.read())

json_file_location = '/home/api-user/storagesite/static/leetcode-solutions.json'

with open(json_file_location, 'r') as f:
    full_dict = json.loads(f.read())

TOKEN = token_dict['token']

intents = Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = discord.Client(intents=intents)

yes_emoji = '<:checkmark:1198881518819475456>'
no_emoji = '<:x_:1198881520224571482>'

# entries of the form (new_key : str, new_item : dict)
submission_queue = []

@bot.event
async def on_ready():
    print('Bot connected as', bot.user)

def insert_submission(submission):
    new_key, new_item = submission
    full_dict[new_key] = new_item[new_key]
    with open(json_file_location, 'w') as f:
        f.write(json.dumps(full_dict))

def remove_submission(key):
    try:
        del full_dict[key]
        with open(json_file_location, 'w') as f:
            f.write(json.dumps(full_dict))
        return True
    except:
        return False

@bot.event
async def on_message(message):
    # pop keys
    if message.content.startswith('pop'):
        try:
            to_undo = message.content[3:][1:-1]
        except:
            await message.channel.send('Syntax for this command is `pop(key)`, where `key` is the key you want to remove.')
            return
        if remove_submission(to_undo):
            await message.channel.send('Successfully removed item with key {}.'.format(to_undo))
        else:
            await message.channel.send('Sorry, unable to remove item with key {}.'.format(to_undo))
        return
    if (not message.webhook_id) and message.author.bot: return
    if (not str(message.channel.id) == '1198832620109307944'): return
    try:
        new_item = json.loads(message.content)
        # get new key
        new_key = list(new_item.keys())[0]
        if new_key in full_dict:
            submission_queue.append((new_key, new_item))
            confirmation_message = await message.channel.send('This item is already in the JSON file. Replace?')
            emojis = [yes_emoji, no_emoji]
            for emoji in emojis:
                await confirmation_message.add_reaction(emoji)
        else:
            await message.channel.send('Adding new item...')
            if insert_submission((new_key, new_item)):
                await message.channel.send('Successfully added new item: ' + new_key)
            else:
                await message.channel.send('Failed to add new item: ' + new_key)
    except Exception as e:
        await message.channel.send('Sorry, something went wrong. Apparently it was: ' + repr(e)) 

@bot.event
async def on_raw_reaction_add(reaction):
    print('Detected reaction')
    channel = bot.get_channel(reaction.channel_id)
    print('Channel:', channel)
    emoji = reaction.emoji
    print('Emoji:', emoji)
    user = bot.get_user(reaction.user_id)
    print('User:', user)
    if user is None or user.bot:
        print('User was None or bot')
        return
    message = await channel.fetch_message(reaction.message_id)
    message_user = message.author
    print('Message user:', message_user)
    if not message_user.bot:
        print('Message user was not bot')
        return
    if str(emoji) == yes_emoji:
        await channel.send('Okay, replacing previous submission with this one.')
        if len(submission_queue) == 0:
            await channel.send('Sorry, timed out. Couldn\'t replace this submission.')
        else:
            insert_submission(submission_queue.pop())
    elif str(emoji) == no_emoji:
        await channel.send('Okay, ignoring this message.')
        if len(submission_queue) == 0:
            await channel.send('Looks like the new submission timed out anyway.')
        else:
            key, content = submission_queue.pop()
            await channel.send(f'Discarded this submission: ' + json.dumps(content))
    else:
        print('The emoji that was detected is not among the valid choices')

bot.run(TOKEN)
