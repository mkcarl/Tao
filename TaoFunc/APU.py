import aiohttp

class Information:
    def __init__(self):
        pass

    async def extract_news(self):
        all_news = []
        news_data = await self._asyncGET("https://api.apiit.edu.my/apspace/student")
        media_data = await self._asyncGET("https://api.apiit.edu.my/apspace/media")

        for news in news_data:
            news_media_id = news["featured_media"]

            for media in media_data:
                if media["id"] != news_media_id:
                    continue
                news_media = media["guid"]["rendered"]
                break

            news_entry = {
                "id" : news["id"],
                "link" : news["link"],
                "title" : news["title"]["rendered"],
                "description" : news["content"]["rendered"],
                "media_link" : news_media
            }

    async def extract_tt(self, intake_code):
        tt_all = await self._asyncGET("https://s3-ap-southeast-1.amazonaws.com/open-ws/weektimetable")
        tt_intake = []
        for class_ in tt_all:
            if class_["INTAKE"] == intake_code:
                tt_intake.append(class_)
        return tt_intake



    @staticmethod
    async def _asyncGET(URL):
        async with aiohttp.ClientSession() as client:
            async with client.get(URL) as resp:
                assert resp.status == 200
                return await resp.json()
