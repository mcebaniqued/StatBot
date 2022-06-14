import discord
from discord.ext import commands
import StatBot_token as BotToken

bot = commands.Bot(
  case_insensitive = True,
  command_prefix = '$',
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
    await ctx.send('Please put required arguments! For more help, type `$help <command>` or `$commandlist`')
  #await bot.process_commands(message)

############
# Commands #
############

#Test command
@bot.command(hidden = True)
async def test(ctx):
  await ctx.send('Hello!')

# Help Commands Category
class Help_Commands(commands.Cog, name = 'Help Commands'):

  @commands.command(
    aliases = ['commands'],
    brief = 'Shows list of commands for available games',
    indent = 4
  )
  async def statcommands(self, ctx):
    await ctx.send("""```  Games                  Commands                                   Example
    Apex Legends           $apexstat <username>                       $apexstat StatBot
    CS:GO                  $csgostat <username>                       $csgostat StatBot
    Fortnite               $fortstat <username>                       $fortstat StatBot
    League of Legends      $lolstat <username>**                      $lolstat StatBot
    Modern Warfare (2019)  $mwstat <username> <game provider>*        $mwstat StatBot psn
    Teamfight Tactics      $tftstat <username>**                      $tftstat StatBot
    Valorant               $valstat <username>#<tagline>              $valstat StatBot#1234
    Vanguard               $vanstat <username> <game provider>*       $vanstat StatBot psn
    Warzone                $wzstat <username> <game provider>*        $wzstat StatBot#1234 battle.net
    
    *Activision and Battle.net require tags for the username
    **LoL and TFT currently supports NA region only```""")

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
    username = username.replace(' ', '%20')
    await ctx.send(f'https://na.op.gg/summoners/na/{username}')

  #Modern Warfare (2019) Stat
  @commands.command(brief = 'Modern Warfare (2019)')
  async def mwstat(self, ctx, username, provider):
    username = username.replace(' ', '%20')
    # Activision
    if provider.lower() == "activision":
      if '#' in username:
        new_user = username.replace('#', '%23')
        await ctx.send(f'https://cod.tracker.gg/modern-warfare/profile/atvi/{new_user}/mp')
      else:
        #Send an error message if tagline not found
        await ctx.send('Please provide the tagline (Example: StatBot#1234)')
    # Battle.net
    elif provider.lower() == "battlenet" or provider.lower() == "battle.net":
      if '#' in username:
        new_user = username.replace('#', '%23')
        await ctx.send(f'https://cod.tracker.gg/modern-warfare/profile/battlenet/{new_user}/mp')
      else:
        #Send an error message if tagline not found
        await ctx.send('Please provide the tagline (Example: StatBot#1234)')
    # Playstation Network
    elif provider.lower() == "psn" or provider.lower() == "playstation":
      await ctx.send(f'https://cod.tracker.gg/modern-warfare/profile/psn/{username}/mp')
    # Xbox Live
    elif provider.lower() == "xbl" or provider.lower() == "xbox" or provider.lower() == "xboxlive":
      await ctx.send(f'https://cod.tracker.gg/modern-warfare/profile/xbl/{username}/mp')
    # Incorrect Provider
    else:
      await ctx.send('Provider not found. Please use: `activision`, `battle.net`, `psn`, or `xbox`.')

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
  async def vanstat(self, ctx, username, provider):
    username = username.replace(' ', '%20')
    # Activision
    if provider.lower() == "activision":
      if '#' in username:
        new_user = username.replace('#', '%23')
        await ctx.send(f'https://cod.tracker.gg/vanguard/profile/atvi/{new_user}/overview')
      else:
        #Send an error message if tagline not found
        await ctx.send('Please provide the tagline (Example: StatBot#1234)')
    # Battle.net
    elif provider.lower() == "battlenet" or provider.lower() == "battle.net":
      if '#' in username:
        new_user = username.replace('#', '%23')
        await ctx.send(f'https://cod.tracker.gg/vanguard/profile/battlenet/{new_user}/overview')
      else:
        #Send an error message if tagline not found
        await ctx.send('Please provide the tagline (Example: StatBot#1234)')
    # Playstation
    elif provider.lower() == "psn" or provider.lower() == "playstation":
      await ctx.send(f'https://cod.tracker.gg/vanguard/profile/psn/{username}/overview')
    # Xbox Live
    elif provider.lower() == "xbl" or provider.lower() == "xbox" or provider.lower() == "xboxlive":
      await ctx.send(f'https://cod.tracker.gg/vanguard/profile/xbl/{username}/overview')
    # Incorrect Provider
    else:
      await ctx.send('Provider not found. Please use: `activision`, `battle.net`, `psn`, or `xbox`.')

  #Warzone Stat
  @commands.command(
    aliases = ['warzonestat'],
    brief = 'Warzone'
  )
  async def wzstat(self, ctx, username, provider):
    username = username.replace(' ', '%20')
    # Activision
    if provider.lower() == "activision":
      if '#' in username:
        new_user = username.replace('#', '%23')
        await ctx.send(f'https://cod.tracker.gg/warzone/profile/atvi/{new_user}/overview')
      else:
        #Send an error message if tagline not found
        await ctx.send('Please provide the tagline (Example: StatBot#1234)')
    # Battle.net
    elif provider.lower() == "battlenet" or provider.lower() == "battle.net":
      if '#' in username:
        new_user = username.replace('#', '%23')
        await ctx.send(f'https://cod.tracker.gg/warzone/profile/battlenet/{new_user}/overview')
      else:
        #Send an error message if tagline not found
        await ctx.send('Please provide the tagline (Example: StatBot#1234)')
    # Playstation
    elif provider.lower() == "psn" or provider.lower() == "playstation":
      await ctx.send(f'https://cod.tracker.gg/warzone/profile/psn/{username}/overview')
    # Xbox Live
    elif provider.lower() == "xbl" or provider.lower() == "xbox" or provider.lower() == "xboxlive":
      await ctx.send(f'https://cod.tracker.gg/warzone/profile/xbl/{username}/overview')
    else:
      await ctx.send('Provider not found. Please use: `activision`, `battle.net`, `psn`, or `xbox`.')

# Add the Categories to the bot
bot.add_cog(Help_Commands())
bot.add_cog(Stat_Commands())

###############
# Run the bot #
###############

bot.run(BotToken.TOKEN)

#TODO: Take account space in username. username argument only takes nonspace strings (MW, VANGUARD, WARZONE)
#TODO: lolstat and tftstat needs region argument
#TODO: Put the help command in Help Command cog/category