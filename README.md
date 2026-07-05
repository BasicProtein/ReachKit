# ReachKit

ReachKit is a small Python toolkit for reading public web pages, RSS feeds, and GitHub resources from command-line workflows.

## Install

```bash
python -m pip install -e .
```

ReachKit requires Python 3.11 or newer.

## CLI

```bash
python -m reachkit --help
python -m reachkit read url https://example.com
python -m reachkit read rss https://example.com/feed.xml --limit 5
python -m reachkit read github owner/repo --path README.md
python -m reachkit search github "agent tools" --limit 5
python -m reachkit doctor
python -m reachkit serve stdio
```

Content commands print plain text by default. Add `--format json` for structured output.

## JSON Output

```json
{
  "source": "web",
  "url": "https://example.com",
  "title": "Example Domain",
  "content_type": "text/html",
  "items": [
    {
      "title": "Example Domain",
      "url": "https://example.com",
      "text": "Example Domain content...",
      "metadata": {}
    }
  ],
  "warnings": []
}
```

## Stdio

`python -m reachkit serve stdio` reads newline-delimited JSON requests from stdin and writes one JSON response per line.

See `examples/stdio-request.jsonl` for a small request set.

## Local Behavior

ReachKit reads public HTTP and HTTPS URLs, public RSS or Atom feeds, and public GitHub API endpoints. It does not use browser sessions, cookies, login-only pages, audio, video, or paid search APIs. A missing `GITHUB_TOKEN` only lowers GitHub rate limits; `doctor` reports it as a warning.
