import discord
from discord.ext import commands, tasks
from TaoFunc import APU, checks
from datetime import datetime


class APU_info(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.newsUpdate.start()


    @commands.group(help="APU related commands.")
    async def apu(self, ctx):
        if ctx.invoked_subcommand is None or ctx.command_failed:
            await ctx.send("Invalid `--apu` command.")

    @apu.command(help="Sends all available news.")
    async def news(self, ctx):
        with ctx.typing():
            history_ids = []
            async for msg in ctx.channel.history(limit=None):
                if len(msg.embeds) != 0:
                    history_ids.append(msg.embeds[0].footer.text)
            data = await APU.Information.extract_news()
            data = data[::-1]
            for news_ in data:
                if str(news_["id"]) in history_ids:
                    continue
                else:
                    news_embed = discord.Embed(
                        colour=discord.Color.dark_red(),
                        title=news_["title"],
                        description=news_["description"][:2047] if len(news_["description"])>2048 else news_["description"],
                        url=news_["link"]
                    )
                    news_embed.set_author(name="APSpace News feed")
                    news_embed.set_image(url=news_["media_link"])
                    news_embed.set_footer(text=news_["id"])
                    await ctx.send(embed=news_embed)

    @apu.command(help="Set the current channel as a specific channel that receives automatic updates.")
    async def set(self, ctx, chType):
        """
        :param chType: str
            eg. "news", "timetable"

        A channel is said to be a news channel if the channel contains an embed, where the footer is "News"
        The news channel will receive updates for APU news at a set interval.
        """
        if chType.lower() == "news":
            embed = discord.Embed(
                title="APU News Channel",
                description="This channel will be used as a news channel that receives automatic updates for events happening in APU. Delete this message/embed if you change your mind."
            )
            embed.set_footer(text="News")
            await ctx.send(embed=embed)

        else:
            ctx.send(f"{chType} is not a valid channel type.{ctx.author.mention}")

        await ctx.message.delete(delay=5)

    @apu.command(help="Start the automatic new updater")
    @commands.check(checks.is_bot_owner())
    async def stop(self, ctx):
        self.newsUpdate.cancel()
        print(f"News update have been stopped by {ctx.author.name} at {datetime.now()}")

    @apu.command(help="Stop the automatic new updater")
    @commands.check(checks.is_bot_owner())
    async def start(self, ctx):
        self.newsUpdate.start()
        print(f"News update have been started by {ctx.author.name} at {datetime.now()}")

    @tasks.loop(hours=6)
    async def newsUpdate(self):
        for guild in self.client.guilds:
            for text_channel in guild.text_channels:
                async for msg in text_channel.history(limit=1000):
                    if len(msg.embeds) == 0:
                        continue
                    else:
                        for e in msg.embeds:
                            if e.footer.text != "News":
                                continue
                            else:
                                cmd = self.client.get_command("apu news")
                                ctx = await self.client.get_context(msg)
                                ctx.command = cmd
                                await ctx.invoke(cmd)
                                print(f"Updated news in {ctx.channel.name} at {datetime.now().strftime('%c')}")
                                break

  def setup(client):
    client.add_cog(APU_info(client))

## TODO:
## Add ping message if there is unhandled exception.
