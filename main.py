import os
import discord
from discord.ext import commands
import datetime
from pretty_help import PrettyHelp, Navigation

client = commands.Bot(command_prefix="--", help_command=PrettyHelp(no_category="Base commands", sort_command=True, color=discord.Color.orange()))

@client.command(help="Yeets the bot out of existance.")
async def yeet(ctx):
    await client.logout()
    print(f"Bot have been yeeted out of existance by {ctx.author.name}")

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

@ext.command(help="Loads the extension(s) into the base bot.")
async def load(ctx, *extensions):
    if len(extensions) > 0:
        if set(extensions).issubset((set(x[:-3] for x in os.listdir("./cogs")))):
            for extension in extensions:
                client.load_extension(f"cogs.{extension}")
            await ctx.send(f"Successfully loaded {', '.join(extensions)}")
        else:
            await ctx.send(f"One or more extension mentioned is not available. Please check the spelling.")
    else:
        await ctx.send("Please specify which extension to load with the command `--ext load <extension>`")

@ext.command(help="Unloads the extension(s) out of the base bot.")
async def unload(ctx, *extensions):
    if len(extensions) > 0:
        if set(extensions).issubset((set(x[:-3] for x in os.listdir("./cogs")))):
            for extension in extensions:
                client.unload_extension(f"cogs.{extension}")
            await ctx.send(f"Successfully unloaded {', '.join(extensions)}")
        else:
            await ctx.send(f"One or more extension mentioned is not available. Please check the spelling.")
    else:
        await ctx.send("Please specify which extension to load with the command `--ext load <extension>`")

@ext.command(help="Shows a list of all the available extensions.")
async def list(ctx):
    extensions_embed = discord.Embed(
        title="Extend functionalities",
        description="This is a list of extensions available. Please use `--ext load <extension>` to load in extension.",
        colour=discord.Color.orange()
    )
    extensions_embed.set_footer(text=f"Generated at: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    extensions = []
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            extensions.append(extension)
    embed_value = ""
    for i in range(len(extensions)):
        embed_value += f"{i+1}. {extensions[i]}\n"
    extensions_embed.add_field(name="Extensions", value=embed_value)


    await ctx.send(embed=extensions_embed)

if __name__ == "__main__":
    token = input("Please insert your bot token : ")
    client.run(token)
