import os
from twilio.rest import Client
import discord
from dotenv import load_dotenv

# So maybe instead of calling me, if it notices a discord noti, it will go check my collected nfts page. If one is there it will automatically list it for sale. 
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# load discord object 
discord_client = discord.Client()
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
# load twilio object
twilio_client = Client(account_sid, auth_token)

@discord_client.event
async def on_ready():
    for guild in discord_client.guilds:
        if guild.name == "USER":
            break
    
    print(
        f'{discord_client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return
    
    call = twilio_client.calls.create(
                        twiml='<Response><Say>Ahoy there!</Say></Response>',
                        to='NUMBER',
                        from_='+14844303657'
                    )
    
    
discord_client.run(TOKEN)

# print(call.sid)
