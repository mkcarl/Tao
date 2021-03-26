from discord.ext import  commands
from TaoFunc import APU


class APU_info(commands.Cog):
    def __init__(self, client):
        self.client = client


def setup(client):
    client.add_cog(APU_info(client))
