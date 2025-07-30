import aiohttp


class AnyAPIClient:
    def __init__(self, task, gemini_key, any_api_key, use_cache=True):
        if not task or not gemini_key or not any_api_key:
            raise ValueError("task, gemini_key, and any_api_key are required.")

        self.payload = {
            "task": task,
            "gemini_key": gemini_key,
            "any_api_key": any_api_key,
            "use_cache": use_cache,
        }

    async def run(self):
        url = "https://www.anyapicreator.space/scrape/" 
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=self.payload) as response:
                    return await response.json()
        except Exception as e:
            return {"error": str(e)}
