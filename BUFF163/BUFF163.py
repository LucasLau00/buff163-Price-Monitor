from discord.embeds import Embed
import discord
from discord import app_commands
from discord import ext
from discord.ext import commands, tasks
import json
from tabulate import tabulate
from datetime import datetime, timedelta
from dhooks import Embed, Webhook
import requests
import time
import concurrent.futures

token = ("") # CHANGE YOUR BOT TOKEN HERE

client = commands.Bot(command_prefix="!",intents=discord.Intents.all())
client.remove_command('help')
SCLogo = "" # CHANGE TO IMAGE LINK

# Set Discord Webhook
hook = Webhook("")
loghook = Webhook("")

UserAgent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

# Change directory names & all
USER = "Administrator"
IDFilePath = f'C:/Users/{USER}/Desktop/BUFF163/IDList.txt'
BuffDataFilePath = f'C:/Users/{USER}/Desktop/BUFF163/BuffData.json'

MonitorIDList = []

def FetchIDs():
    print(f"[{datetime.now()}] | BUFF163 | Loading IDs")
    global MonitorIDList
    IDFile = open(IDFilePath, "rt") 
    ALLIDFileData = IDFile.read()
    IDFile.close()
    MonitorIDList = ALLIDFileData.split('\n')

def SaveNewIDs():
    print(f"[{datetime.now()}] | BUFF163 | Saving New IDs")
    for MonitorID in MonitorIDList:
        MonitorID = str(MonitorID)
        with open(BuffDataFilePath, 'r+') as f:
            savejsondata = json.load(f)
        
        # Check if ID is in JSONFILE
        if MonitorID not in savejsondata:
            try:
                # Adding Preset into jsonFile
                BUFFLink = f"https://buff.163.com/api/market/goods/sell_order?allow_tradable_cooldown=1&appid=730&goods_id={MonitorID}&page_num=1&page_size=5"

                BUFF_Req = requests.get(BUFFLink, headers=UserAgent)
                if BUFF_Req.status_code == 200:
                    BUFF_ReqJson = json.loads(BUFF_Req.text)
                    try:
                        itemName = str(BUFF_ReqJson['data']['goods_infos'][f'{MonitorID}']['market_hash_name'])
                    except:
                        itemName = "N/A"

                    try:
                        itemPrice = str(BUFF_ReqJson['data']['items'][0]['price'])
                    except:
                        itemPrice = "0"

                    ADDSKUDATA = {MonitorID: {"name": itemName, "price": itemPrice}}
                    savejsondata.update(ADDSKUDATA)

                    with open(BuffDataFilePath, 'w') as f2:
                        json.dump(savejsondata, f2, indent=4)
                else:
                    loghook.send(f"{MonitorID} | Error1 When Saving")
            except Exception as e:
                loghook.send(f"{MonitorID} | Error2 When Saving | {e}")

def UpdateIDs():
    print(f"[{datetime.now()}] | BUFF163 | Updating Saved IDs")
    for MonitorID in MonitorIDList:
        MonitorID = str(MonitorID)
        
        try:
            # Adding Preset into jsonFile
            BUFFLink = f"https://buff.163.com/api/market/goods/sell_order?allow_tradable_cooldown=1&appid=730&goods_id={MonitorID}&page_num=1&page_size=5"

            BUFF_Req = requests.get(BUFFLink, headers=UserAgent)
            if BUFF_Req.status_code == 200:
                BUFF_ReqJson = json.loads(BUFF_Req.text)

                try:
                    itemPrice = str(BUFF_ReqJson['data']['items'][0]['price'])
                except:
                    itemPrice = "0"

                with open(BuffDataFilePath, 'r+') as f:
                    jsondata = json.load(f)


                if itemPrice != "0":
                    jsondata[f'{MonitorID}']['price'] = itemPrice
                
                    with open(BuffDataFilePath, 'w') as f2:
                        json.dump(jsondata, f2, indent=4)

            else:
                loghook.send(f"{MonitorID} | Error1 When Updating")

        except Exception as e:
            loghook.send(f"{MonitorID} | Error2 When Saving | {e}")

def MonitorIDs(MonID):
    MonitorID = str(MonID)
    
    try:
        # Adding Preset into jsonFile
        BUFFLink = f"https://buff.163.com/api/market/goods/sell_order?allow_tradable_cooldown=1&appid=730&goods_id={MonitorID}&page_num=1&page_size=5"

        BUFF_Req = requests.get(BUFFLink, headers=UserAgent)
        if BUFF_Req.status_code == 200:
            BUFF_ReqJson = json.loads(BUFF_Req.text)

            try:
                itemPrice = str(BUFF_ReqJson['data']['items'][0]['price'])
            except:
                itemPrice = "0"

            with open(BuffDataFilePath, 'r+') as f:
                jsondata = json.load(f)

            olditemPrice = str(jsondata[f'{MonitorID}']['price'])
            if itemPrice != olditemPrice:
                jsondata[f'{MonitorID}']['price'] = itemPrice
                
                restockembed = Embed(title=f"{str(jsondata[f'{MonitorID}']['name'])}",url= f"https://buff.163.com/goods/{MonitorID}",
                description=f"Price Changes to Item",color=15987699 ,timestamp = 'now')

                try:
                    itemImage = str(BUFF_ReqJson['data']['items'][0]['asset_info']['info']['inspect_en_url'])
                except:
                    itemImage = SCLogo

                try:
                    itemFloat = str(BUFF_ReqJson['data']['items'][0]['asset_info']['paintwear'])
                except:
                    itemFloat = "N/A"
                
                try:
                    itemPattern = str(BUFF_ReqJson['data']['items'][0]['asset_info']['info']['phase_data'])
                except:
                    itemPattern = "N/A"
                
                try:
                    steamPrice = str(BUFF_ReqJson['data']['goods_infos'][f'{MonitorID}']['steam_price_cny'])
                except:
                    steamPrice = "0"

                try:
                    assetID3D = str(BUFF_ReqJson['data']['items'][0]['asset_info']['assetid'])
                    item3D = f"https://buff.163.com/market/csgo_inspect/3d?assetid={assetID3D}"
                except:
                    item3D = "https://buff.163.com/market/csgo_inspect/3d?assetid="
                
                try:
                    cooldownStatus = str(BUFF_ReqJson['data']['items'][0]['asset_info']['has_tradable_cooldown'])
                    if cooldownStatus.upper() == "TRUE":
                        cooldownStatus2 = ":white_check_mark: ON COOLDOWN :white_check_mark:"
                    elif cooldownStatus.upper() == "FALSE":
                        cooldownStatus2 = ":x: NO COOLDOWN :x:"
                except:
                    cooldownStatus2 = ":question: N/A :question:"

                restockembed.add_field(name="NEW Price",value=f"{itemPrice} RMB", inline=True)
                restockembed.add_field(name="OLD Price",value=f"{olditemPrice} RMB", inline=True)
                restockembed.add_field(name="STEAM Price",value=f"{steamPrice} RMB", inline=True)
                restockembed.add_field(name='Item Float', value=f'{itemFloat}', inline=True)
                if itemPattern != "N/A":
                    restockembed.add_field(name='Pattern', value=f'{itemPattern}', inline=True)
                
                restockembed.add_field(name='Tradable', value=cooldownStatus2, inline=False)
                restockembed.add_field(name='Inspect Link', value=f'[3D Inspect]({item3D})', inline=False)

                restockembed.set_image(url=itemImage)
                restockembed.set_footer(text=f'@novaaa | BUFF-163 | <!add [id]>', icon_url =SCLogo)
                hook.send(embed=restockembed)

                with open(BuffDataFilePath, 'w') as f2:
                    json.dump(jsondata, f2, indent=4)


        else:
            loghook.send(f"{MonitorID} | Error1 When Monitoring")

    except Exception as e:
        loghook.send(f"{MonitorID} | Error2 When Monitoring | {e}")

def CheckMonitorID():
    print(f"[{datetime.now()}] | BUFF163 | Starting Threads")
    # Can increase the max_workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for MonID in MonitorIDList:
            try:
                executor.submit(MonitorIDs, MonID)
                time.sleep(1)
            except Exception as e:
                print(f"[{datetime.now()}] | BuffThreads | Error {e}")
    print(f"[{datetime.now()}] | BUFF163 | Ending Threads")

@tasks.loop(seconds=60)
async def BUFFOverall():
    print(f"[{datetime.now()}] | BUFF163 | BUFFOverall START")
    FetchIDs()
    SaveNewIDs()
    CheckMonitorID()
    print(f"[{datetime.now()}] | BUFF163 | BUFFOverall END")

@client.command()
async def add(ctx, id):
    try:
        id = int(id)
        id = str(id)
    
        PIDfile = open(IDFilePath, "rt") 
        ALLPIDfiledata = PIDfile.read()
        PIDfile.close()
        PIDfiledata = ALLPIDfiledata.split('\n')
        ALLPIDList = PIDfiledata

        if id not in ALLPIDList:
            PIDfile = open(IDFilePath, "a") 
            ADDNEWPID = PIDfile.write(f"\n{id}")
            PIDfile.close()
            await ctx.send(f"{id} added.")
        else:
            await ctx.send(f"{id} already stored.")
    except:
        await ctx.send(f"{id} not stored.")

@client.command()
async def rem(ctx, id):
    try:
        id = int(id)
        id = str(id)

        PIDfile = open(IDFilePath, "rt") 
        ALLPIDfiledata = PIDfile.read()
        PIDfile.close()
        PIDfiledata = ALLPIDfiledata.split('\n')
        ALLPIDList = PIDfiledata

        if id in ALLPIDList:
            PIDfile = open(IDFilePath, "w") 
            REMOVEPID = ALLPIDfiledata.replace(f"\n{id}","")
            PIDfile.write(REMOVEPID)
            PIDfile.close()

            PIDfile = open(IDFilePath, "rt") 
            ALLPIDfiledata = PIDfile.read()
            PIDfile.close()
            PIDfiledata = ALLPIDfiledata.split('\n')
            ALLPIDList = PIDfiledata
            if id in ALLPIDList:
                await ctx.send(f"{id} not removed.")
            else:
                await ctx.send(f"{id} removed.")
        else:
            await ctx.send(f"{id} not stored.")
    except:
        await ctx.send(f"{id} not removed.")

@client.command()
async def show(ctx): 

    PIDfile = open(IDFilePath, "rt") 
    ALLPIDfiledata = PIDfile.read()
    PIDfile.close()
    PIDfiledata = ALLPIDfiledata.split('\n')
    ALLPIDList = PIDfiledata
    ALLPIDList = "\n".join(ALLPIDList)
    await ctx.send(ALLPIDList)

@client.command()
async def file(ctx): 
    await ctx.send(file=discord.File(rf'C:/Users/{USER}/Desktop/BUFF163/BuffData.json'))

@client.event
async def on_ready():
    print("BUFF Client is ready!")
    FetchIDs()
    SaveNewIDs()
    UpdateIDs()
    BUFFOverall.start()

client.run(token)