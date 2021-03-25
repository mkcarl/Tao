import aiohttp

class OxfordDictionary:
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    async def define(self, word):
        """
        returns a dictionary
        """
        # get data from oxford dictionary
        endpoint = "entries"
        language_code = "en-us"
        word_id = word
        url = "https://od-api.oxforddictionaries.com/api/v2/" + endpoint + "/" + language_code + "/" + word_id.lower()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"app_id": self.app_id, "app_key": self.app_key}) as r:
                assert r.status == 200
                data = await r.json()

        # convert and extract useful data
        definitions = {}
        for result in data["results"]:
            for lexicalEntry in result["lexicalEntries"]:
                lexicalCategory = lexicalEntry["lexicalCategory"]["text"]
                for entry in lexicalEntry["entries"]:
                    meanings = []
                    for sense in entry["senses"]:
                        wordDefinition = ""
                        wordSemantic = ""
                        wordExample = ""
                        try:
                            for definition in sense["definitions"]:
                                wordDefinition = definition
                        except KeyError:
                            break
                        try:
                            for semanticClass in sense["semanticClasses"]:
                                wordSemantic = semanticClass["text"]
                        except KeyError:
                            wordSemantic = None
                        try:
                            for example in sense["examples"]:
                                wordExample = example["text"]
                        except KeyError:
                            wordExample = None
                        meaning = {"semantic": wordSemantic, "definition": wordDefinition, "example": wordExample}
                        meanings.append(meaning)
                definitions[f"{lexicalCategory}"] = meanings
        return definitions
