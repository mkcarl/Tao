import discord
from discord.ext import  commands
from TaoFunc import APU


class APU_info(commands.Cog):
    def __init__(self, client):
        self.client = client

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
                    news_embed.set_image(url=news_["media_link"])
                    news_embed.set_footer(text=news_["id"])
                    await ctx.send(embed=news_embed)

def setup(client):
    client.add_cog(APU_info(client))
