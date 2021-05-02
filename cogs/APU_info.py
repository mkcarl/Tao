import discord
from discord.ext import commands, tasks
from TaoFunc import APU, checks
from datetime import datetime
import datetime as dt
import asyncio

class APU_info(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.newsUpdate.start()
        self.holUpdate.start()


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
                description="This channel will be used as a news channel that receives automatic updates for events "
                            "happening in APU. Delete this message/embed if you change your mind."
            )
            embed.set_footer(text="News")
            await ctx.send(embed=embed)
        elif chType.lower() == "holidays":
            embed = discord.Embed(
                title="APU Holidays Channel",
                description="This channel will be used as a reminder for upcoming holidays for APU."
                            " Reminder will be sent 7 days in advance."
                            " Delete this message/embed if you change your mind."
            )
            embed.set_footer(text="Holidays")
            await ctx.send(embed=embed)
        else:
            ctx.send(f"`{chType}` is not a valid channel type.{ctx.author.mention}")

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
    @newsUpdate.error
    async def newsUpdate_err(self, ctx, err):
        owner = self.client.fetch_user(self.client.owner_id)
        owner.send("Some error in automatic update. Please check the instance for more details.")
        print(err)

    async def next_holiday(self):
        today = dt.date.today()
        all_holiday = await APU.Information.extract_holiday()
        for holiday in all_holiday:
            holiday["holiday_start_date"] = datetime.strptime(holiday["holiday_start_date"], "%Y-%m-%d")
            holiday["holiday_end_date"] = datetime.strptime(holiday["holiday_end_date"], "%Y-%m-%d")
        all_holiday = [hol for hol in all_holiday if hol["holiday_start_date"] > datetime.now()]
        all_holiday.sort(key=lambda x: x["holiday_start_date"])

        return all_holiday[0]

    @apu.command()
    async def holiday(self, ctx):
        next_hol = await self.next_holiday()
        holiday_embed = discord.Embed(
            title=f"{next_hol['holiday_name']}",
            description=f"{next_hol['holiday_description']}",
            colour=discord.Colour.from_rgb(38, 166, 154)
        )
        holiday_embed.set_author(name="APU holiday updater")
        holiday_embed.add_field(name="Start date", value=f"{next_hol['holiday_start_date'].strftime('%d-%m-%Y')}", inline=True)
        holiday_embed.add_field(name="End date", value=f"{next_hol['holiday_end_date'].strftime('%d-%m-%Y')}", inline=True)
        duration = (next_hol['holiday_start_date'] - next_hol['holiday_end_date']).days + 1
        daysuntil = (next_hol['holiday_start_date'] - datetime.today()).days
        holiday_embed.add_field(name="Duration", value=f"{duration} {'days' if duration>1 else 'day'}", inline=True)
        holiday_embed.add_field(name="Countdown", value=f"{daysuntil} {'days' if duration>1 else 'day'}", inline=True)

        await ctx.send(embed=holiday_embed)

    @tasks.loop(hours=24)
    async def holUpdate(self):
        print("holiday task fired")
        next_hol = await self.next_holiday()
        days_until = (next_hol['holiday_start_date'] - datetime.today()).days
        if days_until == 7:
            for guild in self.client.guilds:
                for text_channel in guild.text_channels:
                    async for msg in text_channel.history(limit=1000):
                        if len(msg.embeds) == 0:
                            continue
                        else:
                            for e in msg.embeds:
                                if e.footer.text != "Holidays":
                                    continue
                                else:
                                    cmd = self.client.get_command("apu holiday")
                                    ctx = await self.client.get_context(msg)
                                    ctx.command = cmd
                                    await ctx.invoke(cmd)
                                    print(f"Updated holidays in {ctx.channel.name} at {datetime.now().strftime('%c')}")


    @holUpdate.error
    async def holUpdate_err(self, ctx, err):
        owner = self.client.fetch_user(self.client.owner_id)
        owner.send("Some error in automatic holiday update. Please check the instance for more details.")
        print(err)

    @holUpdate.before_loop
    async def before_holUpdate(self):
        for _ in range(60*60*24):
            if datetime.now().hour == 0:
                break
            else:
                print("minute is still not 3")
                await asyncio.sleep(1)

def setup(client):
    client.add_cog(APU_info(client))

