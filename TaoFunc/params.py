import discord_argparse as da


cartoonify = da.ArgumentConverter(
            url=da.OptionalArgument(
                str,
                doc="URL of the image.",
                default=''
            ),
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