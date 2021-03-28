from discord.ext import commands

def is_bot_owner():
    def predicate(ctx):
        return ctx.author.id == ctx.bot.owner_id
    return commands.check(predicate)