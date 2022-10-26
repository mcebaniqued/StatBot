# StatBot
Discord bot that sends a link of a stat tracker site of specific games.

#### Helpful Commands:
`$help` - lists out available commands  
`$statcommands` - more in depth list of available games to use

#### Current Games Available (6/14/2022):
- Apex Legends
- CS:GO
- Fortnite
- League of Legends
- Modern Warfare (2019)
- Teamfight Tactics (NA region only)
- Valorant
- Vanguard
- Warzone

---

#### Update Oct 13, 2022:
Rather than sending external link to well known player stat websites, I am working on using APIs to gather data and send it as an embedded message on Discord. I'm currently using [Riot API](https://developer.riotgames.com/)/[RiotWatcher](https://riot-watcher.readthedocs.io/en/latest/) for LoL, TFT, Val, and LoR. Once that's knocked out, I'll work on other games.

Also, [Heroku](https://www.heroku.com/) is getting rid of their free Dynos that was letting me host StatBot for free so I'm gonna have to pull StatBot out until I feel that it's polished and I'll find another site to host it.
