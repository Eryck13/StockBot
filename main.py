import json
import aiohttp
import discord
from disputils import BotEmbedPaginator
import datetime
from discord.ext import commands,tasks
import urllib.parse


validranges = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]


with open("config.json", "r") as config:
    data = json.load(config)
    token = data["Token"]
    prefix = data["Prefix"]
        
    client = commands.Bot(command_prefix=str(prefix),case_insensitive=True)
    client.remove_command('help')

@client.command()
async def ticker(ctx,ticker:str):
    try:
        url="https://query1.finance.yahoo.com/v8/finance/chart/{}?symbol={}&period1=1653192000&period2={}&useYfid=true&interval=1d&includePrePost=true&events=div|split|earn&lang=en-CA&region=CA&crumb=y.I3QERsNxs&corsDomain=ca.finance.yahoo.com".format(ticker,ticker,str(datetime.datetime.timestamp(datetime.datetime.now())))
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.7",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "referrer": "https://ca.finance.yahoo.com/",
            "referrerPolicy": "no-referrer-when-downgrade",
            "body": "null",
            "method": "GET",
            "mode": "cors",
            "credentials": "include"
        }

        async with aiohttp.ClientSession() as sessioncur:
            async with sessioncur.get(url,headers=headers) as get:
                jsonreq = json.loads(await get.text())    
    except:
        print("failed")

client.run(token)
        
        