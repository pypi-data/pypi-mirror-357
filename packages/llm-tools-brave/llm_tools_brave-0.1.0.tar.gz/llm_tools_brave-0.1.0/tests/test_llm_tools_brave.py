from unittest.mock import Mock, patch

import pytest
import httpx

from llm_tools_brave import BraveTools


@pytest.fixture
def brave_tools():
    """Create BraveTools instance for testing."""
    return BraveTools()


@pytest.fixture
def mock_web_response():
    """Mock Brave web search response."""
    return {
        "web": {
            "results": [
                {
                    "title": "Test Web Result",
                    "url": "https://example.com",
                    "description": "This is a test description",
                    "published_date": "2024-01-01",
                    "extra_snippets": ["Important snippet 1", "Important snippet 2"]
                }
            ]
        }
    }


@pytest.fixture
def mock_image_response():
    """Mock Brave image search response."""
    return {
        "results": [
            {
                "title": "Test Image",
                "url": "https://example.com/image.jpg",
                "source": "example.com",
                "thumbnail": {"src": "https://example.com/thumb.jpg"},
                "properties": {"width": 800, "height": 600}
            }
        ]
    }


@pytest.fixture
def mock_news_response():
    """Mock Brave news search response."""
    return {
        "results": [
            {
                "title": "Test News Article",
                "url": "https://news.example.com/article",
                "description": "Breaking news description",
                "age": "2 hours ago",
                "meta_url": {"hostname": "news.example.com"}
            }
        ]
    }


@pytest.fixture
def mock_video_response():
    """Mock Brave video search response."""
    return {
        "results": [
            {
                "title": "Test Video",
                "url": "https://video.example.com/watch",
                "description": "Video description",
                "age": "1 day ago",
                "duration": "5:30",
                "meta_url": {"hostname": "video.example.com"},
                "thumbnail": {"src": "https://video.example.com/thumb.jpg"}
            }
        ]
    }


class TestBraveWebSearch:
    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_web_search_basic(self, mock_client, mock_get_key, mock_web_response, brave_tools):
        """Test basic web search functionality."""
        # Setup mocks
        mock_get_key.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.json.return_value = mock_web_response
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        # Call function
        result = brave_tools.web_search("test query")

        # Verify API calls
        mock_get_key.assert_called_once_with(
            alias="brave", env="BRAVE_API_KEY"
        )

        # Verify output format
        assert "Title: Test Web Result" in result
        assert "URL: https://example.com" in result
        assert "Description: This is a test description" in result
        assert "Published: 2024-01-01" in result
        assert "- Important snippet 1" in result
        assert "- Important snippet 2" in result
        assert "---------" in result

    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_web_search_with_parameters(self, mock_client, mock_get_key, mock_web_response, brave_tools):
        """Test web search with custom parameters."""
        mock_get_key.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.json.return_value = mock_web_response
        mock_response.raise_for_status.return_value = None
        mock_client_instance = mock_client.return_value.__enter__.return_value
        mock_client_instance.get.return_value = mock_response

        # Call with custom parameters
        brave_tools.web_search(
            query="python tutorials",
            num_results=5,
            country="us",
            search_lang="en",
            freshness="pw",
            include_domains=["github.com", "stackoverflow.com"],
            exclude_domains=["example.com"]
        )

        # Verify the request was made with correct parameters
        call_args = mock_client_instance.get.call_args
        assert call_args[1]["params"]["q"] == "python tutorials -site:example.com"
        assert call_args[1]["params"]["count"] == 5
        assert call_args[1]["params"]["country"] == "us"
        assert call_args[1]["params"]["search_lang"] == "en"
        assert call_args[1]["params"]["freshness"] == "pw"
        assert call_args[1]["params"]["site"] == "site:github.com OR site:stackoverflow.com"

    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_web_search_empty_results(self, mock_client, mock_get_key, brave_tools):
        """Test web search with no results."""
        mock_get_key.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.json.return_value = {"web": {"results": []}}
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = brave_tools.web_search("nonexistent query")
        assert result == "No results found."

    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_web_search_network_error(self, mock_client, mock_get_key, brave_tools):
        """Test web search handles network errors by returning error strings."""
        mock_get_key.return_value = "test_api_key"
        mock_client.return_value.__enter__.return_value.get.side_effect = Exception("Network error")

        result = brave_tools.web_search("test query")
        assert "Error performing web search:" in result
        assert "Failed to connect to Brave API" in result

    @patch("llm_tools_brave.llm.get_key")
    def test_web_search_missing_api_key(self, mock_get_key, brave_tools):
        """Test web search raises exception when API key is missing."""
        mock_get_key.return_value = None

        with pytest.raises(ValueError, match="Brave API key not found. Please set it using: llm keys set brave"):
            brave_tools.web_search("test query")


class TestBraveImageSearch:
    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_image_search_basic(self, mock_client, mock_get_key, mock_image_response, brave_tools):
        """Test basic image search functionality."""
        mock_get_key.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.json.return_value = mock_image_response
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = brave_tools.image_search("test image")

        assert "Title: Test Image" in result
        assert "URL: https://example.com/image.jpg" in result
        assert "Source: example.com" in result
        assert "Thumbnail: https://example.com/thumb.jpg" in result
        assert "Dimensions: 800x600" in result

    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_image_search_empty_results(self, mock_client, mock_get_key, brave_tools):
        """Test image search with no results."""
        mock_get_key.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = brave_tools.image_search("nonexistent image")
        assert result == "No image results found."


class TestBraveNewsSearch:
    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_news_search_basic(self, mock_client, mock_get_key, mock_news_response, brave_tools):
        """Test basic news search functionality."""
        mock_get_key.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.json.return_value = mock_news_response
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = brave_tools.news_search("test news")

        assert "Title: Test News Article" in result
        assert "URL: https://news.example.com/article" in result
        assert "Description: Breaking news description" in result
        assert "Age: 2 hours ago" in result
        assert "Source: news.example.com" in result

    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_news_search_with_freshness(self, mock_client, mock_get_key, mock_news_response, brave_tools):
        """Test news search with freshness parameter."""
        mock_get_key.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.json.return_value = mock_news_response
        mock_response.raise_for_status.return_value = None
        mock_client_instance = mock_client.return_value.__enter__.return_value
        mock_client_instance.get.return_value = mock_response

        brave_tools.news_search("breaking news", freshness="pd")

        call_args = mock_client_instance.get.call_args
        assert call_args[1]["params"]["freshness"] == "pd"


class TestBraveVideoSearch:
    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_video_search_basic(self, mock_client, mock_get_key, mock_video_response, brave_tools):
        """Test basic video search functionality."""
        mock_get_key.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.json.return_value = mock_video_response
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = brave_tools.video_search("test video")

        assert "Title: Test Video" in result
        assert "URL: https://video.example.com/watch" in result
        assert "Description: Video description" in result
        assert "Age: 1 day ago" in result
        assert "Duration: 5:30" in result
        assert "Source: video.example.com" in result
        assert "Thumbnail: https://video.example.com/thumb.jpg" in result

    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_video_search_empty_results(self, mock_client, mock_get_key, brave_tools):
        """Test video search with no results."""
        mock_get_key.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = brave_tools.video_search("nonexistent video")
        assert result == "No video results found."


class TestBraveToolsCommon:
    @patch("llm_tools_brave.llm.get_key")
    def test_make_request_headers(self, mock_get_key, brave_tools):
        """Test that _make_request sets correct headers."""
        mock_get_key.return_value = "test_api_key"

        with patch("llm_tools_brave.httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"results": []}
            mock_response.raise_for_status.return_value = None
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            brave_tools._make_request("web/search", {"q": "test"})

            call_args = mock_client.return_value.__enter__.return_value.get.call_args
            headers = call_args[1]["headers"]

            assert headers["Accept"] == "application/json"
            assert headers["Accept-Encoding"] == "gzip"
            assert headers["X-Subscription-Token"] == "test_api_key"

    @patch("llm_tools_brave.llm.get_key")
    def test_missing_api_key_error(self, mock_get_key, brave_tools):
        """Test that a clear error is raised when API key is not set."""
        mock_get_key.return_value = None

        with pytest.raises(ValueError, match="Brave API key not found. Please set it using: llm keys set brave"):
            brave_tools._make_request("web/search", {"q": "test"})

    @patch("llm_tools_brave.llm.get_key")
    def test_empty_api_key_error(self, mock_get_key, brave_tools):
        """Test that a clear error is raised when API key is empty."""
        mock_get_key.return_value = ""

        with pytest.raises(ValueError, match="Brave API key not found. Please set it using: llm keys set brave"):
            brave_tools._make_request("web/search", {"q": "test"})

    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_http_error_422_auth_failure(self, mock_client, mock_get_key, brave_tools):
        """Test that 422 HTTP errors raise exceptions for invalid API key."""
        mock_get_key.return_value = "invalid_api_key"
        mock_response = Mock()
        mock_response.status_code = 422
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.HTTPStatusError(
            "API Error", request=Mock(), response=mock_response
        )

        with pytest.raises(ValueError, match="Brave API rejected the request \\(422\\)"):
            brave_tools._make_request("web/search", {"q": "test"})

    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_http_error_401_auth_failure(self, mock_client, mock_get_key, brave_tools):
        """Test that 401 HTTP errors raise exceptions for authentication failure."""
        mock_get_key.return_value = "invalid_api_key"
        mock_response = Mock()
        mock_response.status_code = 401
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.HTTPStatusError(
            "API Error", request=Mock(), response=mock_response
        )

        with pytest.raises(ValueError, match="Brave API authentication failed \\(401\\)"):
            brave_tools._make_request("web/search", {"q": "test"})

    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_http_error_other_status_codes(self, mock_client, mock_get_key, brave_tools):
        """Test that other HTTP errors return error dicts instead of raising exceptions."""
        mock_get_key.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response
        )

        result = brave_tools._make_request("web/search", {"q": "test"})
        assert "error" in result
        assert "Brave API error (500)" in result["error"]

    @patch("llm_tools_brave.llm.get_key")
    @patch("llm_tools_brave.httpx.Client")
    def test_connection_error_handling(self, mock_client, mock_get_key, brave_tools):
        """Test that connection errors return error dicts instead of raising exceptions."""
        mock_get_key.return_value = "test_api_key"
        mock_client.return_value.__enter__.return_value.get.side_effect = Exception("Connection failed")

        result = brave_tools._make_request("web/search", {"q": "test"})
        assert "error" in result
        assert "Failed to connect to Brave API" in result["error"]

    def test_num_results_bounds(self, brave_tools):
        """Test that num_results is properly bounded between 1 and 20."""
        with patch("llm_tools_brave.llm.get_key") as mock_get_key:
            mock_get_key.return_value = "test_api_key"
            with patch("llm_tools_brave.httpx.Client") as mock_client:
                mock_response = Mock()
                mock_response.json.return_value = {"web": {"results": []}}
                mock_response.raise_for_status.return_value = None
                mock_client_instance = mock_client.return_value.__enter__.return_value
                mock_client_instance.get.return_value = mock_response

                # Test lower bound
                brave_tools.web_search("test", num_results=0)
                call_args = mock_client_instance.get.call_args
                assert call_args[1]["params"]["count"] == 1

                # Test upper bound
                brave_tools.web_search("test", num_results=25)
                call_args = mock_client_instance.get.call_args
                assert call_args[1]["params"]["count"] == 20


@pytest.mark.parametrize(
    "freshness_value",
    ["pd", "pw", "pm", "py"]
)
def test_valid_freshness_values(freshness_value, brave_tools):
    """Test that all valid freshness values are accepted."""
    with patch("llm_tools_brave.llm.get_key") as mock_get_key:
        mock_get_key.return_value = "test_api_key"
        with patch("llm_tools_brave.httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"web": {"results": []}}
            mock_response.raise_for_status.return_value = None
            mock_client_instance = mock_client.return_value.__enter__.return_value
            mock_client_instance.get.return_value = mock_response

            brave_tools.web_search("test", freshness=freshness_value)
            call_args = mock_client_instance.get.call_args
            assert call_args[1]["params"]["freshness"] == freshness_value
