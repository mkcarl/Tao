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

    @apu.group(help="Set the current channel as a specific channel that receives automatic updates.")
    async def setch(self, ctx):
        """
        :param ctx: str
            eg. "news", "timetable"

        A channel is said to be a news channel if the channel contains an embed, where the footer is "News"
        The news channel will receive updates for APU news at a set interval.
        """
        if ctx.invoked_subcommand is None or ctx.command_failed:
            await ctx.send("Invalid `--apu` command.")

    @setch.command(help="Set the current channel to a news channel")
    async def news(self, ctx):
        embed = discord.Embed(
            title="APU News Channel",
            description="This channel will be used as a news channel that receives automatic updates for events "
                        "happening in APU. Delete this message/embed if you change your mind."
        )
        embed.set_footer(text="News")
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @setch.command(help="Set the current channel to a holiday update channel")
    async def holidays(self, ctx):
        embed = discord.Embed(
            title="APU Holidays Channel",
            description="This channel will be used as a reminder for upcoming holidays for APU."
                        " Delete this message/embed if you change your mind."
        )
        embed.set_footer(text="Holidays")
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @setch.group(help="Set the current channel to an exam update channel.")
    async def exams(self, ctx: commands.Context):
        is_exam = False
        async for msg in ctx.channel.history(limit=1000):
            if len(msg.embeds) == 0:
                continue
            else:
                for e in msg.embeds:
                    if e.footer.text != "Exams":
                        is_exam = False
                        continue
                    else:
                        is_exam = True
                        break

        if not is_exam:
            embed = discord.Embed(
                title="APU Exam Channel",
                description="This channel will be used as an update for exam timetables for the specified intakes."
            )
            embed.set_footer(text="Exams")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{ctx.author.mention}, this channel is already initiated as an exam channel.", delete_after=5)
        await ctx.message.delete()

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

    async def next_holiday(self, index) -> dict:
        today = dt.date.today()
        all_holiday = await APU.Information.extract_holiday()
        for holiday in all_holiday:
            holiday["holiday_start_date"] = datetime.strptime(holiday["holiday_start_date"], "%Y-%m-%d")
            holiday["holiday_end_date"] = datetime.strptime(holiday["holiday_end_date"], "%Y-%m-%d")
        all_holiday = [hol for hol in all_holiday if hol["holiday_end_date"].date() >= dt.date.today()]
        all_holiday.sort(key=lambda x: x["holiday_end_date"])

        return all_holiday[index]

    @apu.group(help="Displays the closest or ongoing holiday.")
    async def holiday(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            async with ctx.typing():
                next_hol = await self.next_holiday(0)
                holEmbed: discord.Embed = discord.Embed(title=f"{next_hol['holiday_name']}",
                                                        description=f"{next_hol['holiday_description']}",
                                                        colour=discord.Colour.from_rgb(38, 166, 154))
                holEmbed.set_author(name="APU holidays")
                holEmbed.add_field(name="Start date", value=f"{next_hol['holiday_start_date'].strftime('%d %B %Y')}",
                                   inline=True)
                holEmbed.add_field(name="Duration",
                                   value=f"{(next_hol['holiday_end_date'] - next_hol['holiday_start_date']).days + 1} day(s)",
                                   inline=True)
                countdown = (next_hol['holiday_start_date'] - dt.datetime.today()).days + 1
                holEmbed.add_field(name="Countdown", value=f"{str(countdown) + 'day(s)' if countdown > 0 else 'Ongoing'}",
                                   inline=False)
                holEmbed.set_footer(text=f"{next_hol['holiday_id']}")
                await ctx.send(embed=holEmbed)

    @holiday.command(help="Displays the next <index>th holiday. eg: '--apu holiday next 1' will show the next next holiday. ")
    async def next(self, ctx, index):
        async with ctx.typing():
            next_hol = await self.next_holiday(int(index))
            holEmbed: discord.Embed = discord.Embed(title=f"{next_hol['holiday_name']}",
                                                    description=f"{next_hol['holiday_description']}",
                                                    colour=discord.Colour.from_rgb(38, 166, 154))
            holEmbed.set_author(name="APU holidays")
            holEmbed.add_field(name="Start date", value=f"{next_hol['holiday_start_date'].strftime('%d %B %Y')}",
                               inline=True)
            holEmbed.add_field(name="Duration",
                               value=f"{(next_hol['holiday_end_date'] - next_hol['holiday_start_date']).days + 1} day(s)",
                               inline=True)
            countdown = (next_hol['holiday_start_date'] - dt.datetime.today()).days + 1
            holEmbed.add_field(name="Countdown", value=f"{str(countdown) + 'day(s)' if countdown > 0 else 'Ongoing'}",
                               inline=False)
            holEmbed.set_footer(text=f"{next_hol['holiday_id']}")
            await ctx.send(embed=holEmbed)

    @holiday.error
    async def hol_err(self, ctx: commands.Context, err):
        await ctx.reply(f"{ctx.author.mention}, command invalid. Please try again.", delete_after=5)
        print(err)

    @tasks.loop(hours=24)
    async def holUpdate(self):
        next_hol = await self.next_holiday(0)
        for hol_ch in await self._list_channel("Holidays"):
            last_msg: discord.Message = None
            async for msg in hol_ch.history(limit=1, oldest_first=False):
                last_msg = msg

            holEmbed: discord.Embed = discord.Embed(title=f"{next_hol['holiday_name']}",
                                                    description=f"{next_hol['holiday_description']}",
                                                    colour=discord.Colour.from_rgb(38, 166, 154))
            holEmbed.set_author(name="APU holidays")
            holEmbed.add_field(name="Start date", value=f"{next_hol['holiday_start_date'].strftime('%d %B %Y')}",
                               inline=True)
            holEmbed.add_field(name="Duration",
                               value=f"{(next_hol['holiday_end_date'] - next_hol['holiday_start_date']).days + 1} day(s)",
                               inline=True)
            countdown = (next_hol['holiday_start_date'] - dt.datetime.today()).days + 1
            holEmbed.add_field(name="Countdown", value=f"{str(countdown) + 'day(s)' if countdown > 0 else 'Ongoing'}",
                               inline=False)
            holEmbed.set_footer(text=f"{next_hol['holiday_id']}")

            if last_msg.embeds and last_msg.embeds[0].footer.text == str(next_hol["holiday_id"]):
                # current holiday is same as upcoming holiday
                await last_msg.edit(embed=holEmbed)
            else:
                # current holiday is different from upcoming holiday
                await hol_ch.send(embed=holEmbed)

            math_letters = {
                'a': '𝚊',
                'b': '𝚋',
                'c': '𝚌',
                'd': '𝚍',
                'e': '𝚎',
                'f': '𝚏',
                'g': '𝚐',
                'h': '𝚑',
                'i': '𝚒',
                'j': '𝚓',
                'k': '𝚔',
                'l': '𝚕',
                'm': '𝚖',
                'n': '𝚗',
                'o': '𝚘',
                'p': '𝚙',
                'q': '𝚚',
                'r': '𝚛',
                's': '𝚜',
                't': '𝚝',
                'u': '𝚞',
                'v': '𝚟',
                'w': '𝚠',
                'x': '𝚡',
                'y': '𝚢',
                'z': '𝚣',
                'A': '𝖠',
                'B': '𝖡',
                'C': '𝖢',
                'D': '𝖣',
                'E': '𝖤',
                'F': '𝖥',
                'G': '𝖦',
                'H': '𝖧',
                'I': '𝖨',
                'J': '𝖩',
                'K': '𝖪',
                'L': '𝖫',
                'M': '𝖬',
                'N': '𝖭',
                'O': '𝖮',
                'P': '𝖯',
                'Q': '𝖰',
                'R': '𝖱',
                'S': '𝖲',
                'T': '𝖳',
                'U': '𝖴',
                'V': '𝖵',
                'W': '𝖶',
                'X': '𝖷',
                'Y': '𝖸',
                'Z': '𝖹',
                ' ': '‎',
                '(': '❨',
                ')': '❩',
                '[': '［',
                ']': '］'
            }

            new_ch_name = f"{next_hol['holiday_description']} [{str(countdown) + 'day(s)' if countdown > 0 else 'Ongoing'}]"
            transformed_name = ""
            for c in new_ch_name:
                if c in math_letters:
                    transformed_name += math_letters[c]
                else:
                    transformed_name += c
            await hol_ch.edit(
                name=transformed_name)
            print(new_ch_name)

        print(f"Updated holidays at {datetime.now().strftime('%c')}")

    @holUpdate.error
    async def holUpdate_err(self, ctx, err):
        owner = self.client.fetch_user(self.client.owner_id)
        owner.send("Some error in automatic holiday update. Please check the instance for more details.")
        print(err)

    @holUpdate.before_loop
    async def before_holUpdate(self):
        for _ in range(60*60*24):
            if datetime.now().hour == 0:
                print(f"holiday task started at {datetime.now().strftime('%c')}")
                break
            else:
                await asyncio.sleep(1)

    @apu.group()
    async def exam(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            for ch in await self._list_channel("Exams"):
                intakes = []
                async for msg in ch.history(limit=1000):
                    if len(msg.embeds) != 0:
                        for e in msg.embeds:
                            if e.title == "Intake initiated":
                                intakes.append(e.footer.text)

                for intake in intakes:
                    tt = await APU.Information.extract_exam(intake)
                    embed = discord.Embed(
                        title=f"{intake}",
                        description=f"The following is the exam timetable for intake {intake}. "
                                    f"This message will be updated every day. ",
                        colour=discord.Colour.from_rgb(52, 235, 52)
                    )
                    if not tt:
                        embed.add_field(name="Exam timetable for this intake is unavailable.", value="N/A")
                    else:
                        for exam in tt:
                            start_date, start_time = exam['since'].split("T")
                            end_date, end_time = exam['until'].split("T")
                            start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
                            end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
                            days_left = (dt.datetime.today() - start_date).days if dt.datetime.today() > start_date else 0
                            start_time = dt.datetime.strptime(start_time.replace(":", ''), "%H%M%S%z")
                            end_time = dt.datetime.strptime(end_time.replace(":", ''), "%H%M%S%z")
                            embed.add_field(
                                name=f"{exam['subjectDescription']} ({exam['module']})",
                                value=f"**Date** : {start_date.strftime('%d %B %Y')} ({days_left} days left)\n"
                                      f"**Time** : {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')} \n"
                                      f"**Duration** : {(end_time - start_time).seconds//3600}:{str(((end_time - start_time).seconds//60)%60).zfill(2)} hour(s) \n"
                                      f"**Venue** : {exam['venue']} \n"
                                      f"**Assessment Type** : {exam['assessmentType']} \n"
                                      f"**Appraisal Due** :  \n"
                                      f"**Docket Due** :  \n"
                                      f"================\n"
                                      f"**Results date** : "
                                      f"{dt.datetime.strptime(exam['resultDate'], '%Y-%m-%d').strftime('%d %B %Y')}\n"
                                      f"================",
                                inline=False
                            )

                    intake_present = None
                    async for msg in ch.history(limit=100):
                        if len(msg.embeds) != 0:
                            for e in msg.embeds:
                                if e.title == intake:
                                    intake_present = msg

                    if intake_present is None:
                        await ch.send(embed=embed)
                    else:
                        await intake_present.edit(embed=embed)

    @tasks.loop(hours=24)
    async def examUpdate(self):
        for ch in await self._list_channel("Exams"):
            intakes = []
            async for msg in ch.history(limit=1000):
                if len(msg.embeds) != 0:
                    for e in msg.embeds:
                        if e.title == "Intake initiated":
                            intakes.append(e.footer.text)

            for intake in intakes:
                tt = await APU.Information.extract_exam(intake)
                embed = discord.Embed(
                    title=f"{intake}",
                    description=f"The following is the exam timetable for intake {intake}. "
                                f"This message will be updated every day. ",
                    colour=discord.Colour.from_rgb(52, 235, 52)
                )
                if not tt:
                    embed.add_field(name="Exam timetable for this intake is unavailable.", value="")
                else:
                    for exam in tt:
                        start_date, start_time = exam['since'].split("T")
                        end_date, end_time = exam['until'].split("T")
                        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
                        end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
                        days_left = (dt.datetime.today() - start_date).days if dt.datetime.today() > start_date else 0
                        start_time = dt.datetime.strptime(start_time.replace(":", ''), "%H%M%S%z")
                        end_time = dt.datetime.strptime(end_time.replace(":", ''), "%H%M%S%z")
                        embed.add_field(
                            name=f"{exam['subjectDescription']} ({exam['module']})",
                            value=f"**Date** : {start_date.strftime('%d %B %Y')} ({days_left} days left)\n"
                                  f"**Time** : {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')} \n"
                                  f"**Duration** : {(end_time - start_time).seconds // 3600}:{str(((end_time - start_time).seconds // 60) % 60).zfill(2)} hour(s) \n"
                                  f"**Venue** : {exam['venue']} \n"
                                  f"**Assessment Type** : {exam['assessmentType']} \n"
                                  f"**Appraisal Due** :  \n"
                                  f"**Docket Due** :  \n"
                                  f"================\n"
                                  f"**Results date** : "
                                  f"{dt.datetime.strptime(exam['resultDate'], '%Y-%m-%d').strftime('%d %B %Y')}\n"
                                  f"================",
                            inline=False
                        )

                intake_present = None
                async for msg in ch.history(limit=100):
                    if len(msg.embeds) != 0:
                        for e in msg.embeds:
                            if e.title == intake:
                                intake_present = msg

                if intake_present is None:
                    await ch.send(embed=embed)
                else:
                    await intake_present.edit(embed=embed)

        print(f"Updated exam at {datetime.now().strftime('%c')}")

    @examUpdate.error
    async def examUpdate_err(self, ctx, err):
        owner = self.client.fetch_user(self.client.owner_id)
        owner.send("Some error in automatic exam update. Please check the instance for more details.")
        print(err)

    @examUpdate.before_loop
    async def before_examUpdate(self):
        for _ in range(60 * 60 * 24):
            if datetime.now().hour == 0:
                print(f"exam task started at {datetime.now().strftime('%c')}")
                break
            else:
                await asyncio.sleep(1)

    @exam.command(help="Initiate intake to update.")
    async def set(self, ctx: discord.ext.commands.Context, intake: str):
        await ctx.message.delete()
        is_exam = False
        async for msg in ctx.channel.history(limit=1000):
            if len(msg.embeds) == 0:
                continue
            else:
                for e in msg.embeds:
                    if e.footer.text != "Exams":
                        is_exam = False
                        continue
                    else:
                        is_exam = True
                        break

                if is_exam:
                    break

        if is_exam:
            intake_embed = discord.Embed(
                title="Intake initiated",
                description=f"Intake **{intake.upper()}** has been initiated. Updates on exam timetable of this intake "
                            f"will be updated here."
            )
            intake_embed.set_footer(text=intake.upper())
            await ctx.send(embed=intake_embed)

        else:
            await ctx.send("This channel is not set to an exam channel yet. Please do so using the "
                           "command `--apu setch exams`")

    async def _is_channel(self, text_channel: discord.TextChannel, ch_type: str):
        is_correct = None
        async for msg in text_channel.history(limit=1000):
            if len(msg.embeds) == 0:
                continue
            else:
                for e in msg.embeds:
                    if e.footer.text == ch_type:
                        is_correct = msg
                    else:
                        continue
                if is_correct:
                    break
        return is_correct

    async def _list_channel(self, ch_type: str) -> list[discord.TextChannel]:
        channels = []
        for guild in self.client.guilds:
            for text_channel in guild.text_channels:
                if await self._is_channel(text_channel, ch_type):
                    channels.append(text_channel)
                    continue
        return channels



def setup(client):
    client.add_cog(APU_info(client))



