import aiohttp


class Google_Image_Search:
    def __init__(self, api_key, search_engine_id):
        self.api_key = api_key
        self.search_engine_id = search_engine_id

    async def search(self, keywords:str) -> dict:
        data = await self._get_data(keywords)

        images = []
        for item in data["items"]:
            image = {
                "title" : item["title"],
                "link" : item["link"],
                "context" : item["image"]["contextLink"]
            }
            images.append(image)
        return images

    async def _get_data(self, keywords:str) -> dict :
        url = f"https://www.googleapis.com/customsearch/v1?key={self.api_key}&cx={self.search_engine_id}&q={keywords}&searchType=image"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                assert r.status == 200
                return await r.json()

# if __name__ == "__main__":
#     gis = Google_Image_Search("AIzaSyAqfjAm3HxypuIQ8MLZD7NYQfcDBZfGNFg", "b0f9b48ac3612bdd8")
#     async def main():
#         results = await gis.search("laptop")
#         for result in results:
#             print(result["link"])
#     asyncio.run(main())