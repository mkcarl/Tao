import discord
from discord.ext import commands
from TaoFunc import google_image_search


class Google_Image(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.gis = None

    @commands.group(help="Google search related commands.")
    async def gsearch(self, ctx):
        if ctx.invoked_subcommand is None or ctx.command_failed:
            await ctx.send("Invalid `gsearch` command.")

    @gsearch.command(help="Initialises the search engine")
    async def init(self, ctx, api_key, search_engine_id):
        self.gis = google_image_search.Google_Image_Search(api_key, search_engine_id)
        try:
            await self.gis.search("test")
            await ctx.send("Initialisation done.")
        except AssertionError:
            await ctx.send("Test connection have failed. Please check whether the API key and Search Engine ID is correct.")

    @init.error
    async def init_err(self, ctx, err):
        if isinstance(err, commands.MissingRequiredArgument):
            await ctx.send("There is a missing argument. Please check the command again or use `--help gsearch init`")

    @gsearch.command(help="Sends the image link of the specified keywords. \n\t <number> : how many images to send (1-10) \n\t [keywords...] : search keywords")
    async def img(self, ctx, number, *keywords):
        try:
            assert 0 < int(number) <= 10
            assert len(keywords) != 0
            if self.gis is not None:
                with ctx.typing():
                    data = await self.gis.search(' '.join(keywords))

                for image in data[:int(number)]:
                    picEmbed = discord.Embed(
                        colour=discord.Color.dark_green(),
                    )
                    fieldVal = f"More about this image [here]({image['context']})"
                    picEmbed.set_author(name="Tao Image Search")
                    picEmbed.add_field(name=image["title"], value=fieldVal)
                    picEmbed.set_image(url=image["link"])
                    picEmbed.set_footer(text=f"Query requested by : {ctx.author.display_name} \nSearch query : {' '.join(keywords)}")
                    await ctx.send(embed=picEmbed)
            else:
                await ctx.send("Search engine have not been initialised. Please do the `--help gsearch init` for more information.")
        except (AssertionError, ValueError):
            await ctx.send("Invalid parameters. Please use `--help gsearch img` for more information.")

    @img.error
    async def img_err(self, ctx, err):
        if isinstance(err, commands.MissingRequiredArgument):
            await ctx.send("There is a missing argument. Please check the command again or use `--help gsearch img`")

def setup(client):
    client.add_cog(Google_Image(client))
