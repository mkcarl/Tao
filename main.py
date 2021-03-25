import discord
from discord.ext import commands

client = commands.Bot(command_prefix="--")

@client.command()
async def yeet(ctx):
    await client.logout()

@client.listen("on_ready")
async def ready():
    print("Bot successfully deployed.")

@client.listen("on_disconnect")
async def dc():
    print("Bot has been disconnected.")

@client.group(case_insensitive=True)
async def ext(ctx):
    if ctx.invoked_subcommand is None or ctx.command_failed:
        await ctx.send("Invalid `ext` command.")

@ext.command()
async def load(ctx, extensions):
    client.load_extension(f"cogs.{extensions}")

@ext.command()
async def unload(ctx, extensions):
    client.unload_extension(f"cogs.{extensions}")

@ext.command()
async def list(ctx):
    pass

if __name__ == "__main__":
    token = input("Please insert your bot token : ")
    client.run(token)
