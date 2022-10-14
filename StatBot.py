import discord
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError
import asyncio
import requests
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RIOT_TOKEN = os.getenv("RIOT_API_KEY")

watcher = LolWatcher(RIOT_TOKEN)
bot = commands.Bot(
  case_insensitive = True,
  command_prefix = '$',
  strip_after_prefix = True,
  intents=discord.Intents.all()
)

##########
# Events #
##########

#Prints out a message when the bot is ready/online
@bot.event
async def on_ready():
  print('{0.user} is online.'.format(bot))

# Send a message to the user if the required arguments are missing
@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send(
      f'''Correct usage: {ctx.prefix}{ctx.command.name} {ctx.command.signature}
      For more help, type `$help {ctx.command.name}` or `$commandlist`'''
    )
  #await bot.process_commands(message)

############
# Commands #
############

#Test command
@bot.command(hidden = True)
async def test(ctx):
  await ctx.send('Hello!')

@bot.command(hidden = True)
async def args(ctx, *arg):
  await ctx.send(arg)
  print(arg[-1])
  new_str =""
  for i in range(len(arg)-1):
    new_str += arg[i]
    if i < len(arg)-2:
      new_str += " "
  print(new_str)


# Help Commands Category
class Help_Commands(commands.Cog, name = 'Help Commands'):

  @commands.command(
    aliases = ['commands'],
    brief = 'Shows list of commands for available games',
  )
  async def statcommands(self, ctx):
    await ctx.send(
    """```  Games                  Commands                                   Example
    Apex Legends           $apexstat <username>                       $apexstat StatBot
    CS:GO                  $csgostat <username>                       $csgostat StatBot
    Fortnite               $fortstat <username>                       $fortstat StatBot
    League of Legends      $lolstat <username>**                      $lolstat StatBot
    Modern Warfare (2019)  $mwstat <username> <game platform>*        $mwstat StatBot psn
    Teamfight Tactics      $tftstat <username>**                      $tftstat StatBot
    Valorant               $valstat <username>#<tagline>              $valstat StatBot#1234
    Vanguard               $vanstat <username> <game platform>*       $vanstat StatBot psn
    Warzone                $wzstat <username> <game platform>*        $wzstat StatBot#1234 battle.net
    
    *Activision and Battle.net require tags for the username
    **LoL and TFT currently supports NA region only```"""
    )

# Stat Commands Category
class Stat_Commands(commands.Cog, name = "Stat Commands"):

  #Apex Legend Stat
  @commands.command(brief = 'Apex Legends')
  async def apexstat(self, ctx, *, username):
    username = username.replace(' ', '%20')
    await ctx.send(f'https://apex.tracker.gg/apex/profile/origin/{username}/overview')


  #CS:GO Stat
  @commands.command(brief = 'Counter Strike: Global Offensive')
  async def csgostat(self, ctx, *, username):
    username = username.replace(' ', '%20')
    await ctx.send(f'https://tracker.gg/csgo/profile/steam/{username}/overview')

  #Fortnite Stat
  @commands.command(
    aliases = ['fortnitestat', 'fnstat'], 
    brief = 'Fortnite'
  )
  async def fortstat(self, ctx, *, username):
    username = username.replace(' ', '%20')
    await ctx.send(f'https://fortnitetracker.com/profile/all/{username}')

  #League of Legends Stat
  @commands.command(
    aliases = ['leaguestat'], 
    brief = 'League of Legends'
  )
  async def lolstat(self, ctx, *args):
    version = requests.get('https://ddragon.leagueoflegends.com/api/versions.json').json()[0] #Get latest version

    regions = {
      'BR':   'BR1',
      'EUN':  'EUN1',
      'EUW':  'EUW1',
      'JP':   'JP1',
      'KR':   'KR',
      'LAN':  'LA1',
      'LAS':  'LA2',
      'NA':   'NA1',
      'OCE':  'OC1',
      'TR':   'TR1',
      'RU':   'RU1',
    }

    username = ''
    try:
      platformRoutingValue = regions[args[-1].upper()]
    except:
      platformRoutingValue = "NA1"

      for i in range(len(args)):
        username += args[i]
        if i < len(args)-1:
          username += " "
    else:
      platformRoutingValue = regions[args[-1].upper()]    # Requested Region
      
      for i in range(len(args)-1):
        username += args[i]
        if i < len(args)-2:
          username += " "

    try:
      summoner_id = watcher.summoner.by_name(platformRoutingValue, username)      # Grab summoner object based on summoner name
      # print(summoner_id)
    except ApiError as err:
      print(f'Error Code: {err.response.status_code}')
      if err.response.status_code == 404:
        print('This summoner does not exist')
        embed = discord.Embed(title = "This summoner does not exist")
        await ctx.send(embed=embed)
      elif err.reponse.status_code == 429:
        embed = discord.Embed(title = f"There's an error on our end. Please try again in {err.headers['Retry-After']} seconds.")
        await ctx.send(embed=embed)
      else:
        raise
    else:
      summoner = watcher.league.by_summoner(platformRoutingValue, summoner_id['id'])  # Grab all necessary data
      # print(summoner)
      if not summoner:
        errEmbed = discord.Embed(title = "This summoner does not exist")
        await ctx.send(embed=errEmbed)
      else:
        summonerName = summoner_id['name']
        summonerLevel = summoner_id['summonerLevel']                                    # Level

        # Solo/Duo and Flex
        if len(summoner) == 1:
          if summoner[0]['queueType'] == "RANKED_SOLO_5x5":
            summonerSDRank = summoner[0]['tier'].title() + " " + summoner[0]['rank']              # Rank
            summonerSDLeaguePoints = summoner[0]['leaguePoints']                                  # LP
            summonerSDWins = summoner[0]['wins']                                                  # Number of Wins
            summonerSDLosses = summoner[0]['losses']                                              # Number of Losses
            summonerSDWinrate = int(summonerSDWins/(summonerSDWins + summonerSDLosses) * 100)

            summonerFRank = 'Unranked'
            summonerFLeaguePoints = 0
            summonerFWins = 0                                                                     # Number of Wins
            summonerFLosses = 0                                                                   # Number of Losses
            summonerFWinrate = 0

          elif summoner[0]['queueType'] == "RANKED_FLEX_SR":
            summonerSDRank = 'Unranked'                                                           # Rank
            summonerSDLeaguePoints = 0
            summonerSDWins = 0                                                                    # Number of Wins
            summonerSDLosses = 0                                                                  # Number of Losses
            summonerSDWinrate = 0

            summonerFRank = summoner[0]['tier'].title() + " " + summoner[0]['rank']               # Rank
            summonerFLeaguePoints = summoner[0]['leaguePoints']                                   # LP
            summonerFWins = summoner[0]['wins']                                                   # Number of Wins
            summonerFLosses = summoner[0]['losses']                                               # Number of Losses
            summonerFWinrate = int(summonerFWins/(summonerFWins + summonerFLosses) * 100)

        elif len(summoner) == 2:
          if summoner[0]['queueType'] == "RANKED_SOLO_5x5":
            summonerSDRank = summoner[0]['tier'].title() + " " + summoner[0]['rank']              # Rank
            summonerSDLeaguePoints = summoner[0]['leaguePoints']                                  # LP
            summonerSDWins = summoner[0]['wins']                                                  # Number of Wins
            summonerSDLosses = summoner[0]['losses']                                              # Number of Losses
            summonerSDWinrate = int(summonerSDWins/(summonerSDWins + summonerSDLosses) * 100)

            summonerFRank = summoner[1]['tier'].title() + " " + summoner[1]['rank']
            summonerFLeaguePoints = summoner[1]['leaguePoints']                                   # LP
            summonerFWins = summoner[1]['wins']                                                   # Number of Wins
            summonerFLosses = summoner[1]['losses']                                               # Number of Losses
            summonerFWinrate = int(summonerFWins/(summonerFWins + summonerFLosses) * 100)

          else:
            summonerSDRank = summoner[1]['tier'].title() + " " + summoner[0]['rank']              # Rank
            summonerSDLeaguePoints = summoner[1]['leaguePoints']                                  # LP
            summonerSDWins = summoner[1]['wins']                                                  # Number of Wins
            summonerSDLosses = summoner[1]['losses']                                              # Number of Losses
            summonerSDWinrate = int(summonerSDWins/(summonerSDWins + summonerSDLosses) * 100)

            summonerFRank = summoner[0]['tier'].title() + " " + summoner[0]['rank']               # Rank
            summonerFLeaguePoints = summoner[0]['leaguePoints']                                   # LP
            summonerFWins = summoner[0]['wins']                                                   # Number of Wins
            summonerFLosses = summoner[0]['losses']                                               # Number of Losses
            summonerFWinrate = int(summonerFWins/(summonerFWins + summonerFLosses) * 100)

        #TODO: Champion Masteries
        # masteries = watcher.champion_mastery.by_summoner(platformRoutingValue, summoner_id['id'])
        # for i in range(5):
        #   print(masteries[i])

        embed = discord.Embed(
          title = summonerName
        )
        embed.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/{version}/img/profileicon/{summoner_id['profileIconId']}.png")
        embed.add_field(
          name = "Level",
          value = summonerLevel,
          inline = False
        )
        embed.add_field(
          name = "Ranked Solo/Duo",
          value = f'{summonerSDRank} ({summonerSDLeaguePoints} LP)',
          inline = True
        )
        embed.add_field(
          name = '\u200b', 
          value = '\u200b',
          inline = True
        )
        embed.add_field(
          name = "Win/Loss",
          value = f"{summonerSDWins}/{summonerSDLosses} ({summonerSDWinrate}%)",
          inline = True
        )
        embed.add_field(
          name = "Ranked Flex",
          value = f'{summonerFRank} ({summonerFLeaguePoints} LP)',
          inline = True
        )
        embed.add_field(
          name = '\u200b', 
          value = '\u200b',
          inline = True
        )
        embed.add_field(
          name = "Win/Loss",
          value = f"{summonerFWins}/{summonerFLosses} ({summonerFWinrate}%)",
          inline = True
        )
        #TODO: add Top 5 Champions
        # embed.add_field(
        #   name = "Top Champions",
        #   value = f"",
        #   inline = False
        # )

        #TODO: add footer that contains author and timestamp
        # print(ctx.author.display_name)
        # time = datetime.datetime.now()
        # embed.timestamp = time.strftime("%m/%d/%Y, %H:%M:%S")
        # print(time)
        # # embed.set_footer(
        #   text=f'{ctx.author.display_name} | {ctx.datetime.now()}'
        # )

        await ctx.send(embed=embed)

  #Modern Warfare (2019) Stat
  @commands.command(brief = 'Modern Warfare (2019)')
  async def mwstat(self, ctx, username, platform):
    username = username.replace(' ', '%20')
    # Activision
    if platform.lower() == "activision":
      if '#' in username:
        new_user = username.replace('#', '%23')
        await ctx.send(f'https://cod.tracker.gg/modern-warfare/profile/atvi/{new_user}/mp')
      else:
        #Send an error message if tagline not found
        await ctx.send('Please provide the tagline (Example: StatBot#1234)')
    # Battle.net
    elif platform.lower() == "battlenet" or platform.lower() == "battle.net":
      if '#' in username:
        new_user = username.replace('#', '%23')
        await ctx.send(f'https://cod.tracker.gg/modern-warfare/profile/battlenet/{new_user}/mp')
      else:
        #Send an error message if tagline not found
        await ctx.send('Please provide the tagline (Example: StatBot#1234)')
    # Playstation Network
    elif platform.lower() == "psn" or platform.lower() == "playstation":
      await ctx.send(f'https://cod.tracker.gg/modern-warfare/profile/psn/{username}/mp')
    # Xbox Live
    elif platform.lower() == "xbl" or platform.lower() == "xbox" or platform.lower() == "xboxlive":
      await ctx.send(f'https://cod.tracker.gg/modern-warfare/profile/xbl/{username}/mp')
    # Incorrect Platform
    else:
      await ctx.send('Game platform not found. Please use: `activision`, `battle.net`, `psn`, or `xbox`.')

  #Teamfight Tactics Stat
  @commands.command(brief = 'Teamfight Tactics')
  async def tftstat(self, ctx, *, username):
    username = username.replace(' ', '%20')
    await ctx.send(f'https://tracker.gg/tft/profile/riot/NA/{username}/overview')

    # Implement another time
    #valid_regions = ['NA', 'EUW', 'EUNE', 'LAN', 'LAS', 'OCE', 'KR', 'JP', 'RU', 'BR', 'TR']
    #if region in valid_regions:
      #await ctx.send(f'https://tracker.gg/tft/profile/riot/{region}/{username}/overview')
    #else:
      #await ctx.send('Invalid region! Please use one of the following: `NA`, `EUW`, `EUNE`, `LAN`, `LAS`, `OCE`, `KR`, `JP`, `RU`, `BR`, `TR`')

  #Valorant Stat
  @commands.command(
    aliases = ['valostat', 'valorantstat'],
    brief = 'Valorant'
  )
  async def valstat(self, ctx, *, username):
    username = username.replace(' ', '%20')
    if '#' in username:
      new_user = username.replace('#', '%23')
      await ctx.send(f'https://tracker.gg/valorant/profile/riot/{new_user}/overview')
    else:
      #Send an error message if tagline not found
      await ctx.send('Please provide the tagline (Example: StatBot#1234)')

  #Vanguard Stat
  @commands.command(
    aliases = ['vanguardstat'],
    brief = 'Vanguard'
  )
  async def vanstat(self, ctx, username, platform):
    username = username.replace(' ', '%20')
    # Activision
    if platform.lower() == "activision":
      if '#' in username:
        new_user = username.replace('#', '%23')
        await ctx.send(f'https://cod.tracker.gg/vanguard/profile/atvi/{new_user}/overview')
      else:
        #Send an error message if tagline not found
        await ctx.send('Please provide the tagline (Example: StatBot#1234)')
    # Battle.net
    elif platform.lower() == "battlenet" or platform.lower() == "battle.net":
      if '#' in username:
        new_user = username.replace('#', '%23')
        await ctx.send(f'https://cod.tracker.gg/vanguard/profile/battlenet/{new_user}/overview')
      else:
        #Send an error message if tagline not found
        await ctx.send('Please provide the tagline (Example: StatBot#1234)')
    # Playstation
    elif platform.lower() == "psn" or platform.lower() == "playstation":
      await ctx.send(f'https://cod.tracker.gg/vanguard/profile/psn/{username}/overview')
    # Xbox Live
    elif platform.lower() == "xbl" or platform.lower() == "xbox" or platform.lower() == "xboxlive":
      await ctx.send(f'https://cod.tracker.gg/vanguard/profile/xbl/{username}/overview')
    # Incorrect Platform
    else:
      await ctx.send('Game platform not found. Please use: `activision`, `battle.net`, `psn`, or `xbox`.')

  #Warzone Stat
  @commands.command(
    aliases = ['warzonestat'],
    brief = 'Warzone'
  )
  async def wzstat(self, ctx, username, platform):
    username = username.replace(' ', '%20')
    # Activision
    if platform.lower() == "activision":
      if '#' in username:
        new_user = username.replace('#', '%23')
        await ctx.send(f'https://cod.tracker.gg/warzone/profile/atvi/{new_user}/overview')
      else:
        #Send an error message if tagline not found
        await ctx.send('Please provide the tagline (Example: StatBot#1234)')
    # Battle.net
    elif platform.lower() == "battlenet" or platform.lower() == "battle.net":
      if '#' in username:
        new_user = username.replace('#', '%23')
        await ctx.send(f'https://cod.tracker.gg/warzone/profile/battlenet/{new_user}/overview')
      else:
        #Send an error message if tagline not found
        await ctx.send('Please provide the tagline (Example: StatBot#1234)')
    # Playstation
    elif platform.lower() == "psn" or platform.lower() == "playstation":
      await ctx.send(f'https://cod.tracker.gg/warzone/profile/psn/{username}/overview')
    # Xbox Live
    elif platform.lower() == "xbl" or platform.lower() == "xbox" or platform.lower() == "xboxlive":
      await ctx.send(f'https://cod.tracker.gg/warzone/profile/xbl/{username}/overview')
    # Incorrect Platform
    else:
      await ctx.send('Game platform not found. Please use: `activision`, `battlenet`, `psn`, or `xbox`.')

# Add the Categories to the bot
# bot.add_cog(Help_Commands())
# bot.add_cog(Stat_Commands())

###############
# Run the bot #
###############

async def main():
  await bot.add_cog(Help_Commands())
  await bot.add_cog(Stat_Commands())
  await bot.start(DISCORD_TOKEN)

asyncio.run(main())

#TODO: Take account space in username. username argument only takes nonspace strings (MW, VANGUARD, WARZONE)
#TODO: lolstat and tftstat needs region argument
#TODO: Put the help command in Help Command cog/category