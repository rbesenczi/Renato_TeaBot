from twitchio.ext import commands, routines
from datetime import datetime
from aioconsole import ainput
import json, random, os

old_print = print
def timestamped_print(*args, **kwargs): old_print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " |  ", *args, **kwargs)
print = timestamped_print

def load_json_data(data_file):
    if os.path.isfile(data_file):
        with open(data_file, "r", encoding='utf-8') as read_file:
            try:
                return json.load(read_file)
            except ValueError:
                print(f'"{data_file}" is not a valid json!')
                os._exit(0)
    else: 
        print(f'"{data_file}" not found!')
        os._exit(0)

def write_json_data(path, data):
    with open(path, "w") as outfile: json.dump(data, outfile, indent = 4)

def key_listvalue_string(dict):
    #returns a string in this format:   key1: k1value1, k1value2 | key2: k2value1, k2value2 | key3: k3value...
    #use it only on dicts that has lists for its values
    return " | ".join([key + ": " + ", ".join([listvalue for listvalue in dict[key]])  for key in dict])

class Bot(commands.Bot):

    def __init__(self, token, channel, config_file_path, data_file_path):
        self.token = token
        self.channel = channel
        self.botconfig = load_json_data(config_file_path)
        self.botdata = load_json_data(data_file_path)
        self.botdatapath = data_file_path

        self.viewer_cache = {}  # {"user": watchtime, ...}

        super().__init__(token=token, prefix='!', initial_channels=['#' + channel])

    def get_viewers(self):
        return [chtr.name.lower() for chtr in self.get_channel(self.channel).chatters]

    def write_db(self):
        write_json_data(self.botdatapath, self.botdata.copy())

    async def csp_spend(self, ctx, price):
        name = ctx.author.name.lower()

        if name == self.nick.lower() or name == self.channel.lower(): return True

        if(self.botdata['csatornapont'].get(name, 0) >= price):
            self.botdata['csatornapont'][name] -= price
            self.write_db()
            return True
        else:
            await ctx.send(f":( Nincs sajnos hozzá elég csatornapontod, {ctx.author.mention}.")
            return False

    async def event_ready(self):
        self.watchtimer.start()
        print(f'Logged in as - {self.nick} at channel: {self.channel}')
        print(f'User id is: {self.user_id}')
        print("-" * 80)
        await self.get_channel(self.channel).send("Jelen!")
        await self.consoleinputhandler()
    
    async def consoleinputhandler(self):
        while True: #yolo
            """
            #DEBUG SHIZ
            await ainput()
            old_print(f"getv: {self.get_viewers()}")
            old_print(f"api: {self.get_viewers_api()}")
            old_print(f"twio: {self.get_viewers_twio()}")
            """
            await self.get_channel(self.channel).send(await ainput())

    async def event_message(self, message): #bug in twitcho? message.content seem to lose the first character if it is a ':'
        if message.echo:
            print(self.nick, ": ", message.content)

        else:
            print(message.author.display_name, ": ", message.content)
            if "@" + self.nick in message.content:
                message.content = "!info"
            await self.handle_commands(message)

    @routines.routine(minutes=2) #the update period of the site is about 2 minutes
    async def watchtimer(self):
        db_changed = False #no need to write to the disk unnecessarily
        currentviewerslist = self.get_viewers()

        #remove the bot and the streamer from the viewers
        if self.nick.lower() in currentviewerslist: currentviewerslist.remove(self.nick.lower())
        if self.channel.lower() in currentviewerslist: currentviewerslist.remove(self.channel.lower())

        #remove the viewers who are no longer watching from the list
        #self.viewer_cache stores the viewers list from the last iteration with the recorded watchtime
        for tempviewer in self.viewer_cache.copy(): #this needs to be a copy, removing items while iterating trough is not a good idea
            if tempviewer not in currentviewerslist: del self.viewer_cache[tempviewer]

        #using .get is necessary here, might be a new user
        for viewer in currentviewerslist:
            self.viewer_cache[viewer] = self.viewer_cache.get(viewer, 0) + 2

            #extra points for extended watchtime
            if self.viewer_cache[viewer] % 5 < 2:
                self.botdata["csatornapont"][viewer] = self.botdata["csatornapont"].get(viewer, 0) + 10
                db_changed = True
            
            if self.viewer_cache[viewer] % 15 < 2:
                self.botdata["csatornapont"][viewer] = self.botdata["csatornapont"].get(viewer, 0) + 50
                db_changed = True
        
        #write the changes to disk
        if(db_changed): self.write_db()

    @commands.command()
    async def keksz(self, ctx: commands.Context, arg=None, arg2=None):
        if arg == None: await ctx.send(f"{ctx.author.mention}, a parancs használata: !keksz <kinek> (<mennyit>), 1db keksz 100 csp-be kerül.")

        else: #has argument
            if arg[0] == '@': arg = arg[1:] #remove mention symbol
            arg = arg.lower()
            if arg in self.get_viewers() or arg in self.botdata["csatornapont"] or arg == self.nick.lower() or arg == self.channel.lower(): #current viewer or name in database
                
                if arg2 == None: #did not specify a number, let's assume it is 1
                    if(await self.csp_spend(ctx, 100)):
                        if arg != self.nick.lower() and arg != self.channel.lower(): #no need to keep track of this
                            self.botdata["csatornapont"][arg] += 100
                            self.write_db()
                        await ctx.send(f"NomNom Jár a keksz @{arg}!")

                elif arg2.isnumeric() and int(arg2) > 0: #integer and greater than zero
                    if(await self.csp_spend(ctx, 100 * int(arg2))):
                        if arg != self.nick.lower() and arg != self.channel.lower(): #no need to keep track of this
                            self.botdata["csatornapont"][arg] += 100 * int(arg2)
                            self.write_db()
                        await ctx.send(f"NomNom Jár {int(arg2)} db keksz @{arg}!")

                else: await ctx.send(f"{ctx.author.mention}, második argumentumnak pozitív egész számot adj meg!") #trying something sneaky huh?
            
            else: await ctx.send(f"Nem található {arg} nevű néző!") #trying something sneaky huh?

    @commands.command()
    async def cheer(self, ctx: commands.Context, arg=None):
        if(arg == None): arg = "1"
        if arg.isnumeric() and int(arg) > 0:
            arg = int(arg)
            if(await self.csp_spend(ctx, arg * 10)):
                await ctx.send(f"HSCheers Cheers! {ctx.author.mention} {arg} cheert küldött!")
        else: await ctx.send(f"{ctx.author.mention} Hibás mennyiség!")

    @commands.command()
    async def játssz(self, ctx: commands.Context, arg=None):
        if(await self.csp_spend(ctx, 10000)):
            if(arg == None):
                await ctx.send(f"PotFriend {ctx.author.mention} azt kéri hogy játssz egy általa választott játékkal!")
            else:
                await ctx.send(f"PotFriend {ctx.author.mention} azt kéri hogy játssz a(z) {ctx.message.content[len(ctx.command.name) + 2:]}-al!")
    
    @commands.command()
    async def programozz(self, ctx: commands.Context, arg=None):
        if(await self.csp_spend(ctx, 15000)):
            if(arg == None):
                await ctx.send(f"EarthDay {ctx.author.mention} ad egy programozási feladatot!")
            else:
                await ctx.send(f"EarthDay {ctx.author.mention} a következő programozási feladatot adta: {ctx.message.content[len(ctx.command.name) + 2:]}")

    @commands.command()
    async def raid(self, ctx: commands.Context, arg=None):
        if(await self.csp_spend(ctx, 3000)):
            if(arg == None):
                await ctx.send(f"TombRaid {ctx.author.mention} Raidelni szeretne!")
            else:
                await ctx.send(f"TombRaid {ctx.author.mention} a következő csatornát Raidelné: {ctx.message.content[len(ctx.command.name) + 2:]}")

    @commands.command()
    async def csp(self, ctx: commands.Context):
        if ctx.author.name.lower() == self.nick.lower() or ctx.author.name.lower() == self.channel.lower():
            await ctx.send(f"Kedves {ctx.author.mention}, végtelen sok csatornapontod van.")
        else:
            await ctx.send(f"Kedves {ctx.author.mention}, {self.botdata['csatornapont'].get(ctx.author.name.lower(), 0)} csatornapontod van.")

    @commands.command()
    async def F(self, ctx: commands.Context, arg=None):
        halalok = self.botconfig["deaths"]

        if arg == None: return await ctx.send("Rip in pepperoni.")
        elif arg == "help": await ctx.send(", ".join(["!F " + halal for halal in halalok]))
        elif arg in halalok: await ctx.send(halalok[arg])
        else: await ctx.send('Rip in pepperoni. - nem ismert elhalálozás, "!F help" a halálokért')

    @commands.command()
    async def parancsok(self, ctx: commands.Context):
        await ctx.send(", ".join(["!" + parancs for parancs in self.commands]))

    @commands.command()
    async def hi(self, ctx: commands.Context):
        await ctx.send(f"{ctx.author.mention} rbesenHi")

    @commands.command()
    async def repo(self, ctx: commands.Context):
        await ctx.send(f"{ctx.author.mention}, itt találod a kódot: https://github.com/rbesenczi/newMSM")

    @commands.command()
    async def guide(self, ctx: commands.Context):
        await ctx.send(f"{ctx.author.mention}, itt találsz egy kis leírást: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/MSM")

    @commands.command()
    async def jelen(self, ctx: commands.Context):
        await ctx.send(f"{ctx.author.mention} rbesenJelen")

    @commands.command()
    async def bug(self, ctx: commands.Context):
        await ctx.send("rbesenBug")

    @commands.command()
    async def hidratálj(self, ctx: commands.Context):
        if(await self.csp_spend(ctx, 200)):
            await ctx.send(f"{ctx.author.mention} kéri, hogy hidratálj! rbesenTea")

    @commands.command()
    async def szia(self, ctx: commands.Context):
        await ctx.send(random.choice(self.botconfig["greetings"]) + ctx.author.mention + "! rbesenHi")

    @commands.command()
    async def info(self, ctx: commands.Context):
        await ctx.send("Kedves " + ctx.author.mention + "! Renato_TeaBot vagyok, egy fejlesztés alatt álló Twitch chatbot. Az alábbi parancsokra válaszolok: " + ", ".join(["!" + parancs for parancs in self.commands]))        

    @commands.command()
    async def tea(self, ctx: commands.Context):
        if (self.botconfig["teavagysor"] == "tea"):
            message = "Ma " + self.botconfig["tea"] + "tea van, kedves " + ctx.author.mention + ". rbesenTea"
        else:
            message = "Ma sör van. !sör"

        await ctx.send(message)

    @commands.command()
    async def sör(self, ctx: commands.Context):
        if (self.botconfig["teavagysor"] == "sor"):
            message = "Ma " + self.botconfig["sor"] + " sör van, kedves " + ctx.author.mention + ". rbesenTea"
        else:
            message = "Ma tea van. !tea"

        await ctx.send(message)

    @commands.command()
    async def menetrend(self, ctx: commands.Context):
        await ctx.send("A heti program, " + ctx.author.mention + ": " + key_listvalue_string(self.botconfig["menetrend"]) + " | Streamek mindig 20.00-tól!")

    @commands.command()
    async def linkek(self, ctx: commands.Context):
        await ctx.send("Hasznos linkek, " + ctx.author.mention + ": " + key_listvalue_string(self.botconfig["linkek"]))

def main():
    auth = load_json_data("../config/auth.json")

    bot = Bot(auth["token"], auth["channel"], "/media/renato/SSD/bot_config.json", "/media/renato/SSD/bot_db.json")
    bot.run()

if __name__ == "__main__":
    main()