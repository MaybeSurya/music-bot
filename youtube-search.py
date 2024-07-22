import requests


class YoutubeSearch:
    def __init__(self, query, max_results=1):
        self.query = query
        self.max_results = max_results
        self.videos = self.search()

    def search(self):
        url = "https://www.youtube.com/results"
        params = {"search_query": self.query}
        response = requests.get(url, params=params)
        videos = []
        for result in response.json()["items"]:
            if result["id"]["kind"] == "youtube#video":
                videos.append(
                    {
                        "title": result["snippet"]["title"],
                        "url_suffix": result["id"]["videoId"],
                    }
                )
            if len(videos) >= self.max_results:
                break
        return videos
