import json
import aiohttp
import discord
import datetime
from discord import Embed
import plotly.express as px
import pandas as pd
import random

with open("config.json", "r") as config:
    data = json.load(config)
    token = data["Token"]
    prefix = data["Prefix"]
    intents = discord.Intents.default()
    intents.members = True    
    client = discord.Client(intents=intents)
    
@client.event
async def on_ready():
    print("ready")
    
@client.event
async def on_message(ticker):
    
    if prefix in ticker.content:
        try: 
            urlchart = "https://query1.finance.yahoo.com/v8/finance/chart/{}?symbol={}&period1=1653192000&period2={}&useYfid=true&interval=1d&includePrePost=true&events=div|split|earn&lang=en-CA&region=CA&crumb=y.I3QERsNxs&corsDomain=ca.finance.yahoo.com".format(ticker.content.replace("$","").upper(),ticker.content.replace("$","").upper(),str(int((datetime.datetime.now() - datetime.datetime.utcfromtimestamp(0)).total_seconds())))
            
            urlticker = "https://query2.finance.yahoo.com/v7/finance/quote?formatted=true&crumb=wkU/diDLxbC&lang=en-US&region=US&symbols={}&fields=messageBoardId,longName,shortName,marketCap,underlyingSymbol,underlyingExchangeSymbol,headSymbolAsString,regularMarketPrice,regularMarketChange,regularMarketChangePercent,regularMarketVolume,uuid,regularMarketOpen,fiftyTwoWeekLow,fiftyTwoWeekHigh,toCurrency,fromCurrency,toExchange,fromExchange,corporateActions&corsDomain=finance.yahoo.com".format(ticker.content.replace("$","").upper())

            headers = {"accept": "*/*","accept-language": "en-US,en;q=0.7","sec-fetch-dest": "empty","sec-fetch-mode": "cors","sec-fetch-site": "same-site","sec-gpc": "1","referrer": "https://ca.finance.yahoo.com/","referrerPolicy": "no-referrer-when-downgrade","body": "null","method": "GET","mode": "cors","credentials": "include"}

            getCdata = await chartData(urlchart,headers)
            
            getTdata = await tickerData(urlticker,headers)
            
            plotted = await plot(getCdata,getTdata['tick'])

            embeds = await embed(getTdata, plotted)
            
            await sendOut(embeds,ticker,plotted)
            

        except Exception as e:
            print("failed {}".format(e))

async def chartData(url,headers):
    
    async with aiohttp.ClientSession() as chartdata:
        async with chartdata.get(url,headers=headers) as get:
            d = {}
        
            chartdata_json = json.loads(await get.text())
            chartdata_json = chartdata_json['chart']['result'][0]
            
            timestamps = chartdata_json["timestamp"]
            
            dates = []
            
            for each in timestamps:
                dates.append(datetime.datetime.fromtimestamp(each).strftime('%Y-%m-%d %H:%M:%S'))
            
            openData = chartdata_json["indicators"]["quote"][0]['open']
            closeData = chartdata_json["indicators"]["quote"][0]['close']
            highData = chartdata_json["indicators"]["quote"][0]['high']
            lowData = chartdata_json["indicators"]["quote"][0]['low']
            volumeData = chartdata_json["indicators"]["quote"][0]['volume']
            
            d["Dates"] = dates
            d["Open"] = openData
            d["Close"] = closeData
            d["High"] = highData
            d["Low"] = lowData
            d["Volume"] = volumeData
    
    return d
    
async def tickerData(url,headers):
    
    async with aiohttp.ClientSession() as tickerdata:
        async with tickerdata.get(url,headers=headers) as get:
            
            ticker_json = json.loads(await get.text())
            ticker_json = ticker_json['quoteResponse']['result'][0]
            
            d = {}
            d['tick'] = ticker_json['symbol']
            d['marketCap'] = ticker_json['marketCap']['fmt']
            d['marketTime'] = ticker_json['regularMarketTime']['fmt']
            d['percentChangedDay'] = ticker_json['regularMarketChangePercent']['fmt']
            d['marketRange'] = ticker_json['regularMarketDayRange']['fmt']
            d['yearlyLowChange'] = ticker_json['fiftyTwoWeekLowChange']['fmt']
            d['percentYearlyLow'] = ticker_json['fiftyTwoWeekHighChangePercent']['fmt']
            d['regMarketHigh'] = ticker_json['regularMarketDayHigh']['fmt']
            d['sharesOut'] = ticker_json['sharesOutstanding']['fmt']
            d['regPrevClose'] = ticker_json['regularMarketPreviousClose']['fmt']
            d['yearlyHigh'] = ticker_json['fiftyTwoWeekHigh']['fmt']
            d['yearlyhighChange'] = ticker_json['fiftyTwoWeekHighChange']['fmt']
            d['yearlyRange'] = ticker_json['fiftyTwoWeekRange']['fmt']
            d['regMarketChange'] = ticker_json['regularMarketChange']['fmt']
            d['yearlyLow'] = ticker_json['fiftyTwoWeekLow']['fmt']
            d['marketVol'] = ticker_json['regularMarketVolume']['fmt']
            d['regMarketLow'] = ticker_json['regularMarketDayLow']['fmt']   
            d['shortName'] = ticker_json['shortName']
            
        return d


    
async def plot(datas,tick):
    
    df = pd.DataFrame(datas)
    
    fig = px.line(df, title="{} Chart".format(tick), x = "Dates", y =["Open","Close","High","Low"])
    fig.update_layout(paper_bgcolor="black",plot_bgcolor="black")

    openImgDir = "{}.jpg".format(tick+str(random.randint(0,1000000)))
    fig.write_image(openImgDir)
    
    df1 = pd.DataFrame(datas)

    fig1 = px.line(df1, title="{} Volume Chart".format(tick), x = "Dates", y ="Volume")
    fig1.update_layout(paper_bgcolor="black",plot_bgcolor="black")

    volImgDir = "{}.jpg".format(tick+str(random.randint(0,1000000)))
    fig1.write_image(volImgDir)

    return openImgDir, volImgDir


async def embed(Tdata,plotted):
    embeds = []
    
    embed = discord.Embed()
    embed1 = discord.Embed()
    embed2 = discord.Embed()

    
    embed.title = "${} Stock Info".format(Tdata['tick'])
    embed.description = "Market statistics and data for {}".format(Tdata['shortName'])
    embed.add_field(name="Ticker", value=Tdata['tick'], inline=True)
    embed.add_field(name="Current Market Time", value=Tdata['marketTime'], inline=True)
    embed.add_field(name="Market Cap", value=Tdata['marketCap'], inline=True)
    embed.add_field(name="24Hr High", value=Tdata['regMarketHigh'], inline=True)
    embed.add_field(name="24hr Low", value=Tdata['regMarketLow'], inline=True)
    embed.add_field(name="24Hr Difference", value=Tdata['regMarketChange'], inline=True)
    embed.add_field(name="24Hr %", value=Tdata['percentChangedDay'], inline=True)
    embed.add_field(name="24Hr Range", value=Tdata['marketRange'], inline=True)
    embed.add_field(name="Market Volume", value=Tdata['marketVol'], inline=True)
    embed.add_field(name="Outstanding Shares", value=Tdata['sharesOut'], inline=True)
    embed.add_field(name="Previous Close", value=Tdata['regPrevClose'], inline=True)
    embed.add_field(name="52w Price Difference", value=Tdata['yearlyLowChange'], inline=True)
    embed.add_field(name="52w %", value=Tdata['percentYearlyLow'], inline=True)  
    embed.add_field(name="52w High", value=Tdata['yearlyHigh'], inline=True)
    embed.add_field(name="52w High Difference", value=Tdata['yearlyhighChange'], inline=True)
    embed.add_field(name="52w Range", value=Tdata['yearlyRange'], inline=True)
    embed.add_field(name="52w Low", value=Tdata['yearlyLow'], inline=True)
    
    embed1.set_image(url="attachment://{}".format(plotted[0]))
    
    embed2.set_image(url="attachment://{}".format(plotted[1]))

    embeds.append(embed)
    embeds.append(embed1)
    embeds.append(embed2)
    
    return embeds

async def sendOut(embeds,ticker,plotted):
    
    await ticker.channel.send(embed=embeds[0])
    
    with open(plotted[0], 'rb') as image1:
        await ticker.channel.send(file=discord.File(image1, filename=plotted[0]))
    
    with open(plotted[1], 'rb') as image2:
        await ticker.channel.send(file=discord.File(image2, filename=plotted[1]))

client.run(token)
        
        