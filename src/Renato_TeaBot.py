from twitchio.ext import commands
import json, csv, random, codecs

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

        with codecs.open("../config/bot_config.json", encoding='utf-8') as config_file:
            botconfig = json.load(config_file)

            message = botconfig["greetings"][random.randint(0,12)] + ctx.author.name + "! rbesenHi"

        await ctx.send(message)

    @commands.command()
    async def info(self, ctx: commands.Context):

        message = "Kedves " + ctx.author.name + "! Renato_TeaBot vagyok, egy fejlesztés alatt álló Twitch chatbot. Az alábbi parancsokra válaszolok: !szia !tea !menetrend. "

        await ctx.send(message)        

    @commands.command()
    async def tea(self, ctx: commands.Context):

        with codecs.open("../config/bot_config.json", encoding='utf-8') as config_file:
            botconfig = json.load(config_file)

        if (botconfig["teavagysor"]=="tea"):
            message = "Ma " + botconfig["tea"] + "tea van, kedves " + ctx.author.name + ". rbesenTea"
        else:
            message = "Ma sör van. !sör"

        await ctx.send(message)

    @commands.command()
    async def sör(self, ctx: commands.Context):

        with codecs.open("../config/bot_config.json", encoding='utf-8') as config_file:
            botconfig = json.load(config_file)

        if (botconfig["teavagysor"]=="sor"):
            message = "Ma " + botconfig["sor"] + " sör van, kedves " + ctx.author.name + ". rbesenTea"
        else:
            message = "Ma tea van. !tea"

        await ctx.send(message)

    @commands.command()
    async def menetrend(self, ctx: commands.Context):

        with codecs.open("../config/bot_config.json", encoding='utf-8') as config_file:
            botconfig = json.load(config_file)

            message = "A heti program, " + ctx.author.name + ": "

            for key in botconfig["menetrend"]:
                message += key + ": "
                for elem in botconfig["menetrend"][key]:
                    message += elem + " | "
                message += " "

            message += " Streamek mindig 20.00-tól!"

        await ctx.send(message)

    @commands.command()
    async def linkek(self, ctx: commands.Context):

        with codecs.open("../config/bot_config.json", encoding='utf-8') as config_file:
            botconfig = json.load(config_file)

            message = "Hasznos linkek, " + ctx.author.name + ": "

            for key in botconfig["linkek"]:
                message += key + ": "
                for elem in botconfig["linkek"][key]:
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
