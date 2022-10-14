import discord
import os
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RIOT_TOKEN = os.getenv("RIOT_API_KEY")
watcher = LolWatcher(RIOT_TOKEN)

bot = commands.Bot(
  case_insensitive = True,
  command_prefix = '$',
  strip_after_prefix = True
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
async def embed(ctx):
  embedMsg = discord.Embed(
    title = "Title",
    description = 'Description',
    color = '#FFFFFF'
  )
  embedMsg.set_thumbnail(url='')
  await ctx.send(embedMsg)

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
  async def lolstat(self, ctx, *, username):
    #username = username.replace(' ', '%20')
    # await ctx.send(f'https://na.op.gg/summoners/na/{username}')

    platformRoutingValue = "NA1"    # Requested Region
    summonerName = username         # Requested Summoner Name

    try:
      summoner_id = watcher.summoner.by_name(platformRoutingValue, summonerName)      # Grab encrypted summoner id
      print(summoner_id['id'])
    except ApiError as err:
      if err.response.status_code == 404:
        await ctx.send('Summoner name not found')
        print(f"Username ({username}) not found")
      elif err.reponse.status_code == 429:
        await ctx.send(f"There's an error on our end. Please try again in {err.headers['Retry-After']} seconds.")
      else:
        raise
    else:
      summoner = watcher.league.by_summoner(platformRoutingValue, summoner_id['id'])  # Grab all necessary data
      summonerLevel = summoner_id['summonerLevel']                              # Level
      # Solo/Duo Queue
      summonerSDRank = summoner[0]['tier'].title() + " " + summoner[0]['rank']              # Rank
      summonerSDWins = summoner[0]['wins']                                                  # Number of Wins
      summonerSDLosses = summoner[0]['losses']                                              # Number of Losses
      summonerSDWinrate = int(summonerSDWins/(summonerSDWins + summonerSDLosses) * 100)

      # Flex Queue
      summonerFRank = summoner[1]['tier'].title() + " " + summoner[0]['rank']              # Rank
      summonerFWins = summoner[1]['wins']                                                  # Number of Wins
      summonerFLosses = summoner[1]['losses']                                              # Number of Losses
      summonerFWinrate = int(summonerFWins/(summonerFWins + summonerFLosses) * 100)

      embed = discord.Embed(
        title = username
      )
      embed.add_field(
        name = "Level",
        value = summonerLevel,
        inline = False
      )
      embed.add_field(
        name = "Solo/Duo Queue",
        value = summonerSDRank,
        inline = True
      )
      embed.add_field(
        name = "Win/Loss",
        value = f"{summonerSDWins}/{summonerSDLosses} ({summonerSDWinrate}%)",
        inline = True
      )
      embed.add_field(
        name = "Flex Queue",
        value = summonerFRank,
        inline = True
      )
      embed.add_field(
        name = "Win/Loss",
        value = f"{summonerFWins}/{summonerFLosses} ({summonerFWinrate}%)",
        inline = True
      )

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
bot.add_cog(Help_Commands())
bot.add_cog(Stat_Commands())

###############
# Run the bot #
###############

bot.run(DISCORD_TOKEN)

#TODO: Take account space in username. username argument only takes nonspace strings (MW, VANGUARD, WARZONE)
#TODO: lolstat and tftstat needs region argument
#TODO: Put the help command in Help Command cog/category