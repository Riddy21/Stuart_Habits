# bot.py
# Now let's try to send a message in the server every time a new member joins the server
# bot.py

# Import essential modules
import os
import discord
import urllib
import requests
import json
from dotenv import load_dotenv


def bot():

    intents = discord.Intents(messages=True, guilds=True)
    # Discord requires the in intent of the bot (ie. this bot requires the ability to message and have access to the server)
    
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print('Bot Connected to Discord!')
        
    @client.event  # Complete a set of instructions in the case of an event
    async def on_message(message):  # Track every message
        print(message.content, "   Author: ", message.author.name)

        # Check if message has content
        if message.content is not None:
            # Print the sender and message content in the console

            # If the message is not sent by a bot
            if not message.author.bot:
                mention = f'{client.user.id}'
                if mention in message.content:
                    # Remove tag from user name and replace space with underscore
                    author = str(message.author.name).replace(" ", "_")
                    # Command the bot to reply to the message
                    server_response = request_to_server(author, str(message.content).replace("<@!939569482312077332>", "").replace("<@939569482312077332>", ""))
                    for msg in server_response:
                        await message.channel.send(f"<@{message.author.id}> {msg}") # Discord Response
    client.run(TOKEN)

# Function Goals
# pass dicord chat text to server as a post request
# return response from gpt3 as a get request




# Function Goals
# pass dicord chat text to server as a post request
# K
# return response from gpt3 as a get request 


def urlencode(text):
    url_text = urllib.parse.quote(text, safe='')
    return url_text

def request_to_server(user, message):
    """
    Function takes the discord user's message and passes to the server and returns it's response
    """
    URL = "http://76.10.149.213:5000/discord/"

    payload = 'From=%s&Body=%s' % (urlencode(user), urlencode(message))
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", URL, headers=headers, data=payload)

    data = response.json()

    json_string = json.dumps(data)
    
    # Load JSOON string into a dictionary, parse dictionary and return response text
    json_dict = json.loads(json_string)
    response_dict = json_dict[0]
    msg = response_dict['Success']
    response = msg
    return response

if __name__ == "__main__":
    bot()