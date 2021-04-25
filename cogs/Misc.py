import asyncio
import os
import re
from collections import Counter
from datetime import datetime

import aiofiles
import aiohttp
import discord
import discord_argparse as da
from discord.ext import commands

from TaoFunc import params
from TaoFunc.cartoonify import Cartoonify


class Misc(commands.Cog):
    def __init__(self, client:discord.Client):
        self.client = client
        self.cartoonify_param_converter = da.ArgumentConverter(
            line=da.OptionalArgument(
                int,
                doc="The line size of the output",
                default=7
            ),
            blur=da.OptionalArgument(
                int,
                doc="The amount of blur for the original image",
                default=7
            ),
            k=da.OptionalArgument(
                int,
                doc="Number of clusters to group the colors. Warning : too high of a k-value will slow down the"
                    "algorithm significantly",
                default=9
            ),
            d=da.OptionalArgument(
                int,
                doc="Decrease the noise in the image by how much. Value > 5 will slow down the algorithm significantly.",
                default=5
            ),
            sigma=da.OptionalArgument(
                int,
                doc="Sigma value, tbh i also dk what this means",
                default=200
            )
        )

    @commands.command(
        help="React the words to the specific message. reactionTxt can only be non-recurring words. eg: quick")
    async def react(self, ctx, msgID, *reactionTxt):
        await ctx.message.delete()
        formattedTxt = ''.join(reactionTxt).lower().strip().replace(" ", '')
        viableReaction = (True if len(Counter(formattedTxt)) == len(formattedTxt) else False) \
                         and \
                         not bool(re.compile(r'[^a-z0-9]').search(
                             formattedTxt))  ## check if all char occurs once AND contain only alphanumeric
        try:
            targetMsg = await ctx.fetch_message(msgID)

            if viableReaction:
                emojiDict = {
                    '0': "\u0030\uFE0F\u20E3",
                    '1': "\u0031\uFE0F\u20E3",
                    '2': "\u0032\uFE0F\u20E3",
                    '3': "\u0033\uFE0F\u20E3",
                    '4': "\u0034\uFE0F\u20E3",
                    '5': "\u0035\uFE0F\u20E3",
                    '6': "\u0036\uFE0F\u20E3",
                    '7': "\u0037\uFE0F\u20E3",
                    '8': "\u0038\uFE0F\u20E3",
                    '9': "\u0039\uFE0F\u20E3",
                    'a': "🇦",
                    'b': "🇧",
                    'c': "🇨",
                    'd': "🇩",
                    'e': "🇪",
                    'f': "🇫",
                    'g': "🇬",
                    'h': "🇭",
                    'i': "🇮",
                    'j': "🇯",
                    'k': "🇰",
                    'l': "🇱",
                    'm': "🇲",
                    'n': "🇳",
                    'o': "🇴",
                    'p': "🇵",
                    'q': "🇶",
                    'r': "🇷",
                    's': "🇸",
                    't': "🇹",
                    'u': "🇺",
                    'v': "🇻",
                    'w': "🇼",
                    'x': "🇽",
                    'y': "🇾",
                    'z': "🇿"
                }
                for c in formattedTxt:
                    await targetMsg.add_reaction(emojiDict[c])
            else:
                msg = await ctx.send(f"Invalid `reactionTxt`.{ctx.author.mention}")
                await msg.delete(delay=3)
        except discord.errors.NotFound:
            msg = await ctx.send(f"Message id: {msgID} not found.{ctx.author.mention}")
            await msg.delete(delay=3)
        except discord.errors.Forbidden:
            msg = await ctx.send(f"I do not have the permission to do so!{ctx.author.mention}")
            await msg.delete(delay=3)
        except discord.errors.HTTPException:
            msg = await ctx.send(f"Operation failed.{ctx.author.mention}")
            await msg.delete(delay=3)

    @commands.command(help="Cartoonify an image.")
    async def cartoon(self, ctx, *, param: params.cartoonify = params.cartoonify.defaults()):
        await self.client.change_presence(
            activity=discord.Activity(name=f"calculations by {ctx.author.name}", type=discord.ActivityType.playing))
        now = datetime.now().strftime('%y%m%d%H%M%S%f')
        async with ctx.typing():
            await asyncio.sleep(1)
            refreshed_msg = await ctx.fetch_message(ctx.message.id)  # get a new message coz sometimes the embeds dont load properly
            if not os.path.exists("./.cartoonInput"):
                os.mkdir("./.cartoonInput")
            input_filename = f"./.cartoonInput/Input_{now}.png"

            if len(refreshed_msg.attachments) != 0:  # If there are attachment
                for img in refreshed_msg.attachments[:1]: # only take the first attachment
                    if "image" in img.content_type and img.content_type != "image/gif":
                        await self._downloadImage(img.url, input_filename)
                    else:
                        await ctx.reply("The attached file is not a valid image.")
                if param["url"] != '':
                    await ctx.reply("Url is ignored.", delete_after=3)

            elif len(refreshed_msg.embeds) != 0:  # Then, check if got attachment
                for embed in refreshed_msg.embeds[:1]:  # only take the first attachment
                    img_url = embed.image.url
                    thumbnail_url= embed.thumbnail.url
                    if img_url != discord.Embed.Empty:
                        await self._downloadImage(img_url, input_filename)
                    elif thumbnail_url != discord.Embed.Empty:
                        await self._downloadImage(thumbnail_url, input_filename)
                    else:
                        await ctx.reply("The url does not contain an image.")

            elif param["url"]!='':
                async with aiohttp.ClientSession() as client:
                    async with client.get(param["url"]) as resp:
                        isImage = "image" in resp.headers["Content-Type"]
                if isImage:
                    await self._downloadImage(param["url"], input_filename)
                else:
                    await ctx.reply("The url does not contain an image.")

            if not os.path.exists("./.cartoonOutput"):
                os.mkdir("./.cartoonOutput")
            output_filename = f"./.cartoonOutput/Output_{now}.png"

            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, Cartoonify.wrapper, input_filename,
                                         param["line"],
                                         param["blur"],
                                         param["k"],
                                         param["d"],
                                         param["sigma"])
            await loop.run_in_executor(None, Cartoonify.save_img, results, output_filename)

        await self.client.change_presence(activity=None)

        await ctx.reply(file=discord.File(output_filename))

    @cartoon.error
    async def cartoon_err(self, ctx, err):
        print(err.__cause__)
        if isinstance(err.__cause__, aiohttp.InvalidURL):
            await ctx.reply(f"URL is invalid, please try again.")
        else:
            await ctx.reply("Oops, some error occurred ehe")

    @commands.command(help="Sends back a response after the specified time")
    async def ping(self, ctx, seconds):
        async with ctx.typing():
            for i in range(int(seconds)):
                print(i)
                await asyncio.sleep(1)

            await ctx.send(f"{ctx.author.mention} Pong!")

    async def _downloadImage(self, url, output_file_name):
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = await r.read()
        async with aiofiles.open(output_file_name, mode="wb") as f:
                await f.write(data)


def setup(client):
    client.add_cog(Misc(client))
