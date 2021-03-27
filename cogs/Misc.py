import discord
from discord.ext import commands
from collections import Counter
import re


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(help="React the words to the specific message. reactionTxt can only be non-recurring words. eg: quick")
    async def react(self, ctx, msgID, reactionTxt):
        formattedTxt = reactionTxt.lower().strip().replace(" ", '')
        viableReaction = (True if len(Counter(formattedTxt))==len(formattedTxt) else False) \
               and \
               not bool(re.compile(r'[^a-z0-9]').search(formattedTxt)) ## check if all char occurs once AND contain only alphanumeric
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
                msg = await ctx.send(f"Invalid `reactionTxt`.")

        except discord.errors.NotFound:
            await ctx.send(f"Message id: {msgID} not found.")
        except discord.errors.Forbidden:
            await ctx.send(f"I do not have the permission to do so!")
        except discord.errors.HTTPException:
            await ctx.send(f"Operation failed.")



def setup(client):
    client.add_cog(Misc(client))