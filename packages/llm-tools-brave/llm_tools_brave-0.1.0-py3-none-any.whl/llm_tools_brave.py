import json
from typing import Literal, Optional
import httpx

import llm


class BraveTools(llm.Toolbox):
    name: str = "Brave Search Tools"

    def _make_request(self, endpoint: str, params: dict) -> dict:
        """Make a request to the Brave Search API."""
        api_key = llm.get_key(
            alias="brave", env="BRAVE_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "Brave API key not found. Please set it using: llm keys set brave"
            )

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,
        }

        url = f"https://api.search.brave.com/res/v1/{endpoint}"

        with httpx.Client() as client:
            try:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 422:
                    raise ValueError(
                        f"Brave API rejected the request (422). This usually means the API key is invalid or the request format is incorrect. "
                        f"Please check your API key with: llm keys set brave YOUR_API_KEY"
                    )
                elif e.response.status_code == 401:
                    raise ValueError(
                        f"Brave API authentication failed (401). Please check your API key with: llm keys set brave YOUR_API_KEY"
                    )
                else:
                    # For other HTTP errors, return a recoverable error message
                    return {"error": f"Brave API error ({e.response.status_code}): {str(e)}"}
            except Exception as e:
                # For connection errors, return a recoverable error message
                return {"error": f"Failed to connect to Brave API: {str(e)}"}

    def web_search(
        self,
        query: str,
        num_results: int = 3,
        country: Optional[str] = None,
        search_lang: Optional[str] = None,
        ui_lang: Optional[str] = None,
        freshness: Optional[Literal["pd", "pw", "pm", "py"]] = None,
        include_domains: Optional[list[str]] = None,
        exclude_domains: Optional[list[str]] = None,
        result_filter: Optional[Literal["web", "news", "videos"]] = None,
    ):
        """Search the web using Brave Search API for high-quality, relevant results.

        Args:
            query: The search query string to find relevant content.
            num_results: Number of search results to return (1-20, default: 3).
            country: Country code to customize search results (e.g., 'us', 'uk').
            search_lang: Language for the search results (e.g., 'en', 'es').
            ui_lang: Language for the user interface elements (e.g., 'en', 'es').
            freshness: Restrict results by age - pd (past day), pw (past week), pm (past month), py (past year).
            include_domains: List of domains to limit search results to.
            exclude_domains: List of domains to exclude from search results.
            result_filter: Filter results by type: 'web', 'news', or 'videos'.
        """
        params = {
            "q": query,
            "count": min(max(num_results, 1), 20),  # Brave API supports 1-20 results
        }

        if country:
            params["country"] = country
        if search_lang:
            params["search_lang"] = search_lang
        if ui_lang:
            params["ui_lang"] = ui_lang
        if freshness:
            params["freshness"] = freshness
        if include_domains:
            params["site"] = " OR ".join(f"site:{domain}" for domain in include_domains)
        if exclude_domains:
            exclude_terms = " ".join(f"-site:{domain}" for domain in exclude_domains)
            params["q"] = f"{query} {exclude_terms}"
        if result_filter:
            params["result_filter"] = result_filter

        # Critical errors (missing API key, auth failures) will raise exceptions
        # Recoverable errors (network issues, etc.) will return error dict
        data = self._make_request("web/search", params)

        # Check if we got an error response
        if "error" in data:
            return f"Error performing web search: {data['error']}"

        output = []
        web_results = data.get("web", {}).get("results", [])

        for result in web_results:
            output.append(f"Title: {result.get('title', 'N/A')}")
            output.append(f"URL: {result.get('url', 'N/A')}")
            output.append(f"Description: {result.get('description', 'N/A')}")

            if result.get("published_date"):
                output.append(f"Published: {result['published_date']}")

            if result.get("extra_snippets"):
                output.append("Extra snippets:")
                for snippet in result["extra_snippets"]:
                    output.append(f"- {snippet}")

            output.append("---------\n")

        return "\n".join(output) if output else "No results found."

    def image_search(
        self,
        query: str,
        num_results: int = 3,
        country: Optional[str] = None,
        search_lang: Optional[str] = None,
        ui_lang: Optional[str] = None,
    ):
        """Search for images using Brave Search API.

        Args:
            query: The search query string to find relevant images.
            num_results: Number of image results to return (1-20, default: 3).
            country: Country code to customize search results (e.g., 'us', 'uk').
            search_lang: Language for the search results (e.g., 'en', 'es').
            ui_lang: Language for the user interface elements (e.g., 'en', 'es').
        """
        params = {
            "q": query,
            "count": min(max(num_results, 1), 20),
        }

        if country:
            params["country"] = country
        if search_lang:
            params["search_lang"] = search_lang
        if ui_lang:
            params["ui_lang"] = ui_lang

        data = self._make_request("images/search", params)

        if "error" in data:
            return f"Error performing image search: {data['error']}"

        output = []
        image_results = data.get("results", [])

        for result in image_results:
            output.append(f"Title: {result.get('title', 'N/A')}")
            output.append(f"Source: {result.get('source', 'N/A')}")

            # Handle URL field - could be direct or in properties
            url = result.get("url")
            if not url and result.get("properties"):
                url = result["properties"].get("url")
            if url:
                output.append(f"URL: {url}")

            # Handle thumbnail
            if result.get("thumbnail") and result["thumbnail"].get("src"):
                output.append(f"Thumbnail: {result['thumbnail']['src']}")

            # Handle dimensions from properties
            if result.get("properties"):
                props = result["properties"]
                if props.get("width") and props.get("height"):
                    output.append(f"Dimensions: {props['width']}x{props['height']}")
            output.append("---------\n")

        return "\n".join(output) if output else "No image results found."

    def news_search(
        self,
        query: str,
        num_results: int = 3,
        country: Optional[str] = None,
        search_lang: Optional[str] = None,
        ui_lang: Optional[str] = None,
        freshness: Optional[Literal["pd", "pw", "pm", "py"]] = None,
    ):
        """Search for news using Brave Search API.

        Args:
            query: The search query string to find relevant news articles.
            num_results: Number of news results to return (1-20, default: 3).
            country: Country code to customize search results (e.g., 'us', 'uk').
            search_lang: Language for the search results (e.g., 'en', 'es').
            ui_lang: Language for the user interface elements (e.g., 'en', 'es').
            freshness: Restrict results by age - pd (past day), pw (past week), pm (past month), py (past year).
        """
        params = {
            "q": query,
            "count": min(max(num_results, 1), 20),
        }

        if country:
            params["country"] = country
        if search_lang:
            params["search_lang"] = search_lang
        if ui_lang:
            params["ui_lang"] = ui_lang
        if freshness:
            params["freshness"] = freshness

        data = self._make_request("news/search", params)

        if "error" in data:
            return f"Error performing news search: {data['error']}"

        output = []
        news_results = data.get("results", [])

        for result in news_results:
            output.append(f"Title: {result.get('title', 'N/A')}")
            output.append(f"URL: {result.get('url', 'N/A')}")
            output.append(f"Description: {result.get('description', 'N/A')}")

            if result.get("age"):
                output.append(f"Age: {result['age']}")
            if result.get("meta_url"):
                output.append(f"Source: {result['meta_url']['hostname']}")

            output.append("---------\n")

        return "\n".join(output) if output else "No news results found."

    def video_search(
        self,
        query: str,
        num_results: int = 3,
        country: Optional[str] = None,
        search_lang: Optional[str] = None,
        ui_lang: Optional[str] = None,
        freshness: Optional[Literal["pd", "pw", "pm", "py"]] = None,
    ):
        """Search for videos using Brave Search API.

        Args:
            query: The search query string to find relevant videos.
            num_results: Number of video results to return (1-20, default: 3).
            country: Country code to customize search results (e.g., 'us', 'uk').
            search_lang: Language for the search results (e.g., 'en', 'es').
            ui_lang: Language for the user interface elements (e.g., 'en', 'es').
            freshness: Restrict results by age - pd (past day), pw (past week), pm (past month), py (past year).
        """
        params = {
            "q": query,
            "count": min(max(num_results, 1), 20),
        }

        if country:
            params["country"] = country
        if search_lang:
            params["search_lang"] = search_lang
        if ui_lang:
            params["ui_lang"] = ui_lang
        if freshness:
            params["freshness"] = freshness

        data = self._make_request("videos/search", params)

        if "error" in data:
            return f"Error performing video search: {data['error']}"

        output = []
        video_results = data.get("results", [])

        for result in video_results:
            output.append(f"Title: {result.get('title', 'N/A')}")
            output.append(f"URL: {result.get('url', 'N/A')}")
            output.append(f"Description: {result.get('description', 'N/A')}")

            if result.get("age"):
                output.append(f"Age: {result['age']}")
            if result.get("duration"):
                output.append(f"Duration: {result['duration']}")
            if result.get("meta_url"):
                output.append(f"Source: {result['meta_url']['hostname']}")
            if result.get("thumbnail"):
                output.append(f"Thumbnail: {result['thumbnail']['src']}")

            output.append("---------\n")

        return "\n".join(output) if output else "No video results found."


@llm.hookimpl
def register_tools(register):
    brave_tools = BraveTools()
    register(brave_tools.web_search, "web_search")
    register(brave_tools.image_search, "image_search")
    register(brave_tools.news_search, "news_search")
    register(brave_tools.video_search, "video_search")
    register(BraveTools, "Brave")
