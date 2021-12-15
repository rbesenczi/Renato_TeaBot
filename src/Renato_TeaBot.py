from twitchio.ext import commands
import json, csv, random

class Bot(commands.Bot):

    def __init__(self, username, token, channel):
        self.token = token
        self.channel = '#' + channel
        super().__init__(token=token, prefix='!', initial_channels=[channel])

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    @commands.command()
    async def szia(self, ctx: commands.Context):

        message = ""

        with open("../config/bot_config.json", "r") as config_file:
            botconfig = json.load(config_file)

            message = botconfig["greetings"][random.randint(0,7)] + ", " + ctx.author.name + "! rbesenHi"

        await ctx.send(message)

    @commands.command()
    async def info(self, ctx: commands.Context):

        message = "Kedves " + ctx.author.name + "! Renato_TeaBot vagyok, egy fejlesztés alatt álló Twitch chatbot. Az alábbi parancsokra válaszolok: !szia !jelen !tea !menetrend. "

        await ctx.send(message)        

    @commands.command()
    async def jelen(self, ctx: commands.Context):

        message = "Kedves " + ctx.author.name + "! Nem szerepelsz a könyvelésben."

        with open("../config/jelenlet.csv", newline='') as konyveles:
            jelenlet = csv.DictReader(konyveles)
            for row in jelenlet:
                if row["name"].lower() == ctx.author.name:
                    message = "Kedves " + ctx.author.name + "! A könyvelésben " + str(row["jelen"]) + " jelenléted van."

        await ctx.send(message)

    @commands.command()
    async def tea(self, ctx: commands.Context):

        with open("../config/bot_config.json", "r") as config_file:
            botconfig = json.load(config_file)

        message = "Ma " + botconfig["tea"] + "tea van, kedves " + ctx.author.name + ". rbesenTea"

        await ctx.send(message)

    @commands.command()
    async def menetrend(self, ctx: commands.Context):

        with open("../config/bot_config.json", "r") as config_file:
            botconfig = json.load(config_file)

            message = "A heti program, " + ctx.author.name + ": "

            for key in botconfig["menetrend"]:
                message += key + ": "
                for elem in botconfig["menetrend"][key]:
                    message += elem + " | "
                message += " "

        await ctx.send(message)

def main():

    with open("../config/auth.json", "r") as read_file:
        data = json.load(read_file)

    username  = data["username"]
    token     = data["token"]
    channel   = data["channel"]

    bot = Bot(username, token, channel)
    bot.run()

if __name__ == "__main__":
    main()
