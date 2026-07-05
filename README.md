# ReachKit

<p align="center">
  <a href="docs/README.zh-CN.md"><img alt="中文" src="https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87-2f81f7?style=flat-square"></a>
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/README-English-2f81f7?style=flat-square"></a>
  <a href="docs/README.ja.md"><img alt="日本語" src="https://img.shields.io/badge/README-%E6%97%A5%E6%9C%AC%E8%AA%9E-2f81f7?style=flat-square"></a>
  <a href="docs/README.ko.md"><img alt="한국어" src="https://img.shields.io/badge/README-%ED%95%9C%EA%B5%AD%EC%96%B4-2f81f7?style=flat-square"></a>
</p>

ReachKit is a Python CLI and library for giving AI agents clean, predictable access to public web pages, RSS or Atom feeds, and GitHub content.

It is built for agent workflows that need retrieval without a browser session, login flow, crawler farm, or paid search stack. Give it a public URL, feed, repository, file path, or GitHub search query. ReachKit returns normalized text records with stable JSON fields that an agent can inspect, cite, store, rank, or pass into another tool.

## Why ReachKit exists

AI agents keep running into the same retrieval problems:

- Search snippets are too thin for reasoning. Agents need page text, feed entries, repository metadata, and file contents, not just a title and URL.
- Web content arrives in different shapes. HTML, plain text, RSS, Atom, and GitHub API payloads all need different parsing before an agent can use them.
- Browser automation is heavy for simple public content. Many jobs only need HTTP, text cleanup, and predictable output.
- Ad hoc scripts are hard to trust. One command prints prose, another prints partial JSON, another mixes warnings into stdout.
- Agent tool calls need contracts. A tool that sometimes returns text, sometimes crashes, and sometimes prints logs is painful to chain.
- Public repositories are part of research. Agents often need README files, repository summaries, language, stars, default branches, and search results from GitHub.
- Local diagnostics matter. A missing GitHub token, a broken HTTPS runtime, or a non UTF-8 console can waste an entire run.

ReachKit focuses on the boring but important layer between "the agent needs public context" and "the agent can reason over clean text".

## Where it fits

There are strong hosted APIs for web search, crawling, JavaScript rendering, Markdown extraction, ranking, and managed research. ReachKit is for the smaller local job that still has to be dependable:

- You already know the public URL, feed, repository, or GitHub query you want to read.
- You want a Python command that can run in CI, local scripts, or an agent sandbox.
- You need stdout to stay machine-readable so another tool can parse it.
- You prefer explicit warnings and typed errors over silent partial output.
- You want public GitHub metadata and text files in the same retrieval path as web pages and feeds.
- You need a low-setup input stage for RAG, summarization, monitoring, or developer research.

In short: use ReachKit when the hard part is not ranking the whole web, but turning known public sources into clean records that agents can trust.

## What it does

ReachKit currently supports:

- Public URL reading for `text/html`, `text/plain`, and other readable `text/*` responses.
- HTML title extraction and readable text cleanup using the Python standard library.
- RSS and Atom feed parsing with normalized entry metadata.
- GitHub repository metadata through the public GitHub REST API.
- GitHub file reading through the contents API, including base64 text files.
- GitHub repository search with stable item fields.
- A `doctor` command for Python version, UTF-8 I/O, HTTPS runtime, GitHub token, and network checks.
- A newline-delimited JSON stdio server for agent tool integration.
- Text and JSON output from content commands.

ReachKit does not try to be a full web crawler. It does not use browser sessions, cookies, login-only pages, social media scraping, audio, video, or paid search APIs.

## Good fits

ReachKit is useful when you are building:

- AI agent tools that need public web page text.
- Retrieval workflows for README files, docs pages, and release feeds.
- Research assistants that read RSS or Atom feeds before summarizing.
- GitHub repository discovery tools for developer agents.
- Local command-line pipelines that need deterministic JSON.
- Stdio tools for agent runtimes that expect request and response objects.
- Lightweight RAG ingestion scripts for public pages and feeds.
- CI checks that monitor public docs, changelogs, feeds, or GitHub files.
- Developer research scripts that need web, feed, and repository context without a browser.

If you need JavaScript rendering, authenticated sites, large-scale crawling, or anti-abuse platform handling, ReachKit is intentionally not that layer.

## Install

ReachKit requires Python 3.11 or newer.

For local development:

```bash
python -m pip install -e .
```

With `uv`, you can keep the runtime isolated:

```bash
uv venv .venv --python 3.11
uv pip install --python .venv/Scripts/python.exe -e . pytest
```

On macOS or Linux, the virtual environment Python path is usually `.venv/bin/python`.

## Quick start

Read a public web page:

```bash
reachkit read url https://example.com --format json
```

Read a feed:

```bash
reachkit read rss https://example.com/feed.xml --limit 5 --format json
```

Read GitHub repository metadata:

```bash
reachkit read github owner/repo --format json
```

Read a public text file from a GitHub repository:

```bash
reachkit read github owner/repo --path README.md --ref main --format json
```

Search public GitHub repositories:

```bash
reachkit search github "agent tools" --limit 5 --format json
```

Check local readiness:

```bash
reachkit doctor
```

Run the stdio tool server:

```bash
reachkit serve stdio
```

## Output contract

Content commands return plain text by default. Add `--format json` to get a stable object:

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

Every content result has:

- `source`: `web`, `rss`, or `github`.
- `url`: the request URL or canonical result URL when available.
- `title`: the page, feed, repository, search, or file title when available.
- `content_type`: the HTTP content type when available.
- `items`: normalized text records.
- `warnings`: non-fatal issues such as `empty_feed` or `non_html_text`.

This shape is intentionally small. Agents can parse it without learning a new schema for every source.

## Stdio integration

`reachkit serve stdio` reads one JSON object per line from stdin and writes one JSON object per line to stdout.

List tools:

```json
{"id":"1","method":"tools/list","params":{}}
```

Call a tool:

```json
{"id":"2","method":"tools/call","params":{"name":"web_read","arguments":{"url":"https://example.com","max_chars":2000}}}
```

Available tools:

- `web_read`: `url`, optional `max_chars`.
- `rss_read`: `url`, optional `limit`.
- `github_read`: `repo`, optional `path`, optional `ref`.
- `github_search`: `query`, optional `limit`.

See `examples/stdio-request.jsonl` for a small request set.

## GitHub access

ReachKit uses public GitHub REST endpoints. You can run without a token, but GitHub rate limits unauthenticated requests more aggressively.

To raise the limit, set:

```bash
GITHUB_TOKEN=your_token_here
```

The token is used only as an HTTP bearer token for GitHub API requests.

## Limits and behavior

- `--format` supports `text` and `json`.
- `--max-chars` defaults to `12000` and accepts values from `1` to `100000`.
- `--limit` defaults to `10` and caps at `50`.
- HTTP uses `http://` and `https://` only.
- The default HTTP timeout is `15` seconds.
- Oversized responses, non-2xx responses, invalid XML, invalid input, and binary GitHub files return user-facing errors.
- `doctor` returns exit code `1` only when a required check fails.

## Why not use a browser?

Browsers are useful when a page needs JavaScript, authentication, or interaction. They are also slower, harder to sandbox, and harder to make deterministic.

ReachKit handles the public-content path first: fetch, parse, normalize, and return a small record. That makes it easier to test and easier to plug into an agent loop.

## Common questions

### What is ReachKit?

ReachKit is a local retrieval toolkit for AI agents. It reads public URLs, RSS or Atom feeds, and GitHub resources, then returns clean text records as plain text or JSON.

### What problem does ReachKit solve for AI agents?

Agents often need fresh public context, but raw web pages, feed XML, and GitHub API payloads are awkward to pass around. ReachKit gives agents one small contract for public retrieval: fetch the content, clean the text, keep useful metadata, and report warnings separately.

### Is ReachKit a web crawler?

No. ReachKit is a focused public content reader. It handles single URLs, feeds, GitHub repository metadata, GitHub text files, and GitHub repository search. It does not crawl whole sites, render JavaScript, or work with login-only content.

### How is ReachKit different from hosted web search APIs?

Hosted search and extraction APIs are useful when you need ranking, scale, managed crawling, JavaScript rendering, or cited research. ReachKit is for the lighter local path: predictable CLI commands, stdio integration, no mandatory paid API, and outputs that are easy to test.

### Can ReachKit feed a RAG pipeline?

Yes, for public pages, feeds, and GitHub resources. ReachKit can turn those inputs into normalized text records that a RAG ingestion script can chunk, embed, store, or score.

### What searches should find this project?

ReachKit is meant for searches like "Python CLI for AI agent web retrieval", "AI agent tool for reading public URLs", "RSS to JSON command line tool", "GitHub repository search CLI JSON", "stdio tools/list tools/call Python server", "public web page to clean text Python", and "GitHub README reader for AI agents".

## Development

Run tests:

```bash
python -m pytest -q
```

Run a smoke check:

```bash
reachkit doctor
reachkit read url https://example.com --format json
```

The test suite uses fixtures and mocked HTTP paths where practical, so routine tests do not depend on live websites.

## License

Apache-2.0. See `LICENSE`.
