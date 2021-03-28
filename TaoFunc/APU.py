import aiohttp
import re


class Information:
    def __init__(self):
        pass

    @staticmethod
    def _cleanHTML(rawhtml):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', rawhtml)
        return cleantext

    @classmethod
    async def extract_news(cls):
        all_news = []
        news_data = await cls._asyncGET("https://api.apiit.edu.my/apspace/student")
        media_data = await cls._asyncGET("https://api.apiit.edu.my/apspace/media")
        slideshow_data = await cls._asyncGET("https://api.apiit.edu.my/apspace/student/slideshow")

        for slideshow in slideshow_data:
            slideshow_media_id = slideshow["featured_media"]

            for media in media_data:
                if media["id"] != slideshow_media_id:
                    continue
                slideshow_media = media["guid"]["rendered"]
                break

            try:
                link = slideshow["post-meta-fields"]["slideshow_url"][0]
            except KeyError:
                link = slideshow["link"]

            slideshow_entry = {
                "id": slideshow["id"],
                "link": link,
                "title": slideshow["title"]["rendered"],
                "description": cls._cleanHTML(slideshow["content"]["rendered"]),
                "media_link": slideshow_media
            }
            all_news.append(slideshow_entry)

        for news in news_data:
            news_media_id = news["featured_media"]

            for media in media_data:
                if media["id"] != news_media_id:
                    continue
                news_media = media["guid"]["rendered"]
                break

            news_entry = {
                "id": news["id"],
                "link": news["link"],
                "title": news["title"]["rendered"],
                "description": cls._cleanHTML(news["content"]["rendered"]),
                "media_link": news_media
            }
            all_news.append(news_entry)
        return all_news


    @classmethod
    async def extract_tt(cls, intake_code):
        tt_all = await cls._asyncGET("https://s3-ap-southeast-1.amazonaws.com/open-ws/weektimetable")
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
