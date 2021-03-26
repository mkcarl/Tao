import discord
from discord.ext import commands
from TaoFunc import DictDefine

class Oxford_Dictionary(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.oxDict = None

    @commands.group(help="English Dictionary.")
    async def ox(self, ctx):
        if ctx.invoked_subcommand is None or ctx.command_failed:
            await ctx.send("Invalid `ox` command.")

    @ox.command(help="Initialise the dictionary.")
    async def init(self, ctx, app_id, app_key):
        self.oxDict = DictDefine.OxfordDictionary(app_id, app_key)
        try:
            await self.oxDict.define("test")
            await ctx.send("Initialisation done.")
        except AssertionError:
            await ctx.send("Test connection have failed. Please check whether the APP ID and APP KEY is correct.")

    @init.error
    async def init_err(self, ctx, err):
        if isinstance(err, commands.MissingRequiredArgument):
            await ctx.send("There is a missing argument. Please check the command again or use `--help ox init`")

    @ox.command(help="Returns the definition of the word with example sentences.")
    async def define(self, ctx, word):
        try:
            if self.oxDict is None:
                await ctx.send("Dictionary have not been initialised. Please do the `--help ox init` for more information.")
            else:
                with ctx.typing():
                    data = await self.oxDict.define(word)

                    definitionEmbed = discord.Embed(
                        colour=discord.Color.green(),
                        title=f"Definition for {word}"
                    )
                    definitionEmbed.set_footer(text=f"Requested by : {ctx.author.display_name}")
                    for k, v in data.items():
                        desc = ""
                        for meaning in v:
                            desc += f"{v.index(meaning)+1}. {meaning['definition']} " \
                                    f"**({meaning['semantic']})** " \
                                    f"\n > *{meaning['example'] if meaning['example'] is not None else 'No example sentence found.'}*\n\n"

                        definitionEmbed.add_field(name=f"==={k}===", value=desc, inline=False)

                await ctx.send(embed=definitionEmbed)
        except AssertionError:
            await ctx.send("No such word.")

    @define.error
    async def define_err(self, ctx, err):
        if isinstance(err, commands.MissingRequiredArgument):
            await ctx.send("Please specify what word you want to define. Please use `--help ox define` for more information")
        elif isinstance(err, AssertionError):
            await ctx.send("No such word.")
        else:
            await ctx.send("Some error occurred.")


def setup(client):
    client.add_cog(Oxford_Dictionary(client))