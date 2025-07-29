# llm-tools-brave

A tool plugin for [LLM](https://llm.datasette.io/) that allows you to search the web using [Brave Search API](https://brave.com/search/api/).

[![PyPI](https://img.shields.io/pypi/v/llm-tools-brave.svg)](https://pypi.org/project/llm-tools-brave/)
[![Changelog](https://img.shields.io/github/v/release/daturkel/llm-tools-brave?include_prereleases&label=changelog)](https://github.com/daturkel/llm-tools-brave/releases)
[![Tests](https://github.com/daturkel/llm-tools-brave/actions/workflows/test.yml/badge.svg)](https://github.com/daturkel/llm-tools-brave/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/daturkel/llm-tools-brave/blob/main/LICENSE)

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/):

```bash
llm install llm-tools-brave
```

## Usage

Create an account at [Brave Search API](https://api-dashboard.search.brave.com/) and get your API key. Add it to llm with `llm keys set brave`.

This plugin provides four search tools which can be bundled together or provided separately.

Use `-T Brave` to include all tools, or use individual tool names: `-T web_search`, `-T image_search`, `-T news_search`, `-T video_search`.

### web_search

Search the web for high-quality, relevant results with descriptions and snippets:

```bash
llm -m claude-4-sonnet -T web_search "search the web to get today's weather in nyc"
```

### image_search

Search for images with metadata and thumbnails:

```bash
llm -m claude-4-sonnet -T image_search "find images of golden retrievers"
```

### news_search

Search for recent news articles with age and source information:

```bash
llm -m claude-4-sonnet -T news_search "latest news about AI developments"
```

### video_search

Search for videos with duration, thumbnails, and source information:

```bash
llm -m claude-4-sonnet -T video_search "python programming tutorials"
```

## Features

- **Web Search**: Get comprehensive web results with descriptions and extra snippets
- **Image Search**: Find images with metadata, dimensions, and thumbnail previews
- **News Search**: Access recent news articles with publication timing
- **Video Search**: Discover videos with duration and preview information
- **Advanced Filtering**: Support for country-specific results, language preferences, freshness filters, and domain inclusion/exclusion
- **Error Handling**: Robust error handling with informative error messages

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

```bash
cd llm-tools-brave
python -m venv venv
source venv/bin/activate
```

Install the dependencies and test dependencies:

```bash
pip install -e '.[test]'
```

To run the tests:

```bash
pytest
```

## Dependencies

- [llm](https://llm.datasette.io/): The LLM CLI tool this plugin extends
- [httpx](https://www.python-httpx.org/): For making HTTP requests to the Brave Search API

## Credits

> [!NOTE]
> This is a fork of [llm-tools-exa](https://github.com/daturkel/llm-tools-exa) by [Dan Turkel](https://github.com/daturkel), converted from the Exa API to Brave Search API. All credit for the original implementation goes to Dan Turkel. This conversion was mostly vibe coded with Claude 4 and Cursor.
