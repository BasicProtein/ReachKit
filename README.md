# ReachKit

<p align="center">
  <a href="docs/README.zh-CN.md"><img alt="中文" src="https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87-2f81f7?style=flat-square"></a>
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/README-English-2f81f7?style=flat-square"></a>
  <a href="docs/README.ja.md"><img alt="日本語" src="https://img.shields.io/badge/README-%E6%97%A5%E6%9C%AC%E8%AA%9E-2f81f7?style=flat-square"></a>
  <a href="docs/README.ko.md"><img alt="한국어" src="https://img.shields.io/badge/README-%ED%95%9C%EA%B5%AD%EC%96%B4-2f81f7?style=flat-square"></a>
</p>

ReachKit gives AI agents a clean internet intake layer: read pages and feeds, inspect GitHub, pull transcripts and metadata, search supported platforms, and return small JSON records an agent can actually use.

Agents are good at reasoning, but they are brittle at retrieval. A raw webpage is noisy. A platform API may need a token. A transcript might exist only when the video exposes timed text. A one-off script may print logs where JSON should be. ReachKit turns those messy edges into predictable CLI commands, stdio tools, provider diagnostics, and explicit setup guidance.

It is built for workflows that need public or explicitly authorized content without hidden browser extraction, login automation, crawler farms, proxy machinery, or silent credential collection. Give it a URL, feed, repository, file path, platform query, post id, stock symbol, podcast feed, or authorized API target. ReachKit returns normalized text records with stable fields that an agent can inspect, cite, store, rank, or pass into another tool.

## Why Agents Need This

AI agents do not fail only because a model is weak. They fail because the input layer is unreliable:

- A search result says a page exists, but the agent still needs the page body before it can reason.
- A feed, GitHub response, transcript, and social post all arrive in different shapes.
- A missing token or local dependency can waste a whole run if the agent discovers it late.
- Browser automation is too heavy when the task only needs HTTP, parsing, and clean output.
- Shell snippets are hard to chain when warnings, logs, and data all share stdout.
- Credentials are risky when tools silently read browser profiles or store token values.

ReachKit handles the input step before reasoning starts: fetch, normalize, warn, and tell the agent what is ready.

## Where It Fits

Use ReachKit when you want a local, inspectable retrieval layer rather than a hosted crawler or a pile of scripts:

- You already know a URL, feed, repository, video, post, stock symbol, or platform query.
- You need stable JSON for an agent loop, RAG ingestion, CI check, or monitoring job.
- You want one result shape across web pages, feeds, GitHub, transcripts, posts, and platform searches.
- You need `doctor` output that says what works, what needs config, and what to do next.
- You prefer explicit environment variables and user-supplied files over hidden session scraping.
- You want the simple path first, with optional rendered-page reads only when you choose them.

ReachKit is not trying to rank the whole internet. It turns known public or explicitly authorized sources into records an agent can trust.

## What You Can Do In Five Minutes

```bash
reachkit setup plan
reachkit channels doctor
reachkit read url https://example.com --format json
reachkit read github owner/repo --path README.md --format json
reachkit serve stdio
```

That gives an agent a quick readiness map, a web reader, a GitHub reader, and a stdio tool server without teaching it a new schema for every source.

## What It Does

| User pain | ReachKit path |
| --- | --- |
| "The agent has a URL but needs usable text." | `reachkit read url`, RSS, podcast feed, and optional rendered-page readers. |
| "The agent needs code and project context." | GitHub repo, file, repository search, issue, pull request, and release readers. |
| "The agent needs platform content in the same shape." | YouTube, X, Xiaohongshu, Bilibili, Reddit, V2EX, LinkedIn, Xueqiu, Facebook, and Instagram readers/searchers. |
| "The run failed because setup was missing." | `setup plan`, `channels doctor`, `auth status`, and fix messages. |
| "The agent runtime wants tools, not prose." | `reachkit serve stdio` with `tools/list` and `tools/call`. |
| "Credentials must stay explicit." | Config stores env var names and user-supplied file paths, not token values. |

ReachKit currently supports:

- Setup planning, local config creation, update guidance, and removal with dry-run and safe modes.
- Channel diagnostics that describe platform capabilities, provider readiness, missing configuration, and suggested fixes.
- Local auth configuration that stores environment variable names and explicit cookie or storage-state paths, not token values.
- Public URL reading for `text/html`, `text/plain`, and other readable `text/*` responses.
- Explicit cookie input for URL reads, using JSON cookie lists, Netscape cookie files, or Playwright storage state files supplied by the user.
- HTML title extraction and readable text cleanup using the Python standard library.
- RSS and Atom feed parsing with normalized entry metadata.
- GitHub repository metadata, file reading, repository search, issues, pull requests, and releases.
- YouTube public transcript reading when timed text is available, plus YouTube metadata and search with an explicit API key.
- X post reading, search, thread-style conversation lookup, and timeline-style query results through the official API with `X_BEARER_TOKEN` or `TWITTER_BEARER_TOKEN`.
- Xiaohongshu open API JSON, note search, note detail, and comments with `XHS_APP_KEY` and `XHS_APP_SECRET`.
- Bilibili public video metadata and public video search.
- Reddit public search, post, and comment JSON reads.
- V2EX hot topics, node topics, topic detail with replies, and user records.
- Podcast RSS metadata and episode records.
- LinkedIn public page text reads.
- Xueqiu quote, stock search, and hot-list records.
- Facebook and Instagram Graph API records when the user supplies explicit access tokens.
- Optional rendered page reading through `reachkit[browser]` for pages the user can access.
- A newline-delimited JSON stdio server for agent tool integration.
- Text and JSON output from content commands.

ReachKit does not try to be a full web crawler. It does not read browser profiles, solve access challenges, operate proxy pools, spoof fingerprints, or silently collect login state. Authenticated paths require explicit environment variables, cookie files, storage-state files, or official API tokens supplied by the user.

## Good Fits

ReachKit is useful when you are building:

- AI agent tools that need public web page text instead of thin snippets.
- Research assistants that collect sources before summarizing or comparing claims.
- RAG ingestion scripts that need predictable records before chunking and embedding.
- Developer agents that inspect README files, docs pages, releases, issues, and repositories.
- Monitoring jobs that watch feeds, changelogs, docs, or public platform records.
- Local command-line pipelines where stdout must stay parseable.
- Agent runtimes that prefer request/response tools over handwritten shell snippets.
- Workflows that need platform-specific content without a new schema per platform.

If you need JavaScript rendering for pages you can access, use the optional browser extra. If you need large-scale crawling, challenge solving, proxy pools, or anti-abuse platform handling, ReachKit is intentionally not that layer.

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

For rendered page reads, install the optional browser extra and the browser runtime:

```bash
python -m pip install -e ".[browser]"
python -m playwright install chromium
```

## Quick start

Plan local setup before changing anything:

```bash
reachkit setup plan
reachkit setup install --dry-run
reachkit setup install --safe
```

Create the default local config:

```bash
reachkit setup install
```

Check platform capability status:

```bash
reachkit channels list
reachkit channels doctor
reachkit auth status
```

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

Search a configured web endpoint:

```bash
reachkit search web "agent tools" --limit 5 --format json
```

Read GitHub issues, pull requests, and releases:

```bash
reachkit read github owner/repo --issue 7 --format json
reachkit read github owner/repo --pull-request 3 --format json
reachkit read github owner/repo --release v1.0.0 --format json
```

Read a YouTube transcript when public timed text is available:

```bash
reachkit read youtube dQw4w9WgXcQ --lang en --format json
reachkit read youtube dQw4w9WgXcQ --metadata --format json
```

Search YouTube with an explicit API key:

```bash
reachkit search youtube "agent tools" --limit 5 --format json
```

Read an X post through the official API:

```bash
reachkit read x 1234567890 --format json
```

Search X through the official API:

```bash
reachkit search x "agent tools" --limit 5 --format json
```

Read Xiaohongshu open API JSON with configured app credentials:

```bash
reachkit read xiaohongshu /api/open/path --param note_id=abc --format json
```

Read public Bilibili video metadata by BV id or av id:

```bash
reachkit read bilibili BV1xx411c7mD --format json
reachkit read bilibili av123456 --format json
```

Search Bilibili:

```bash
reachkit search bilibili "agent tools" --limit 5 --format json
```

Read other public or explicit-token sources:

```bash
reachkit read reddit https://www.reddit.com/r/example/comments/abc/title/ --format json
reachkit search reddit "agent tools" --limit 5 --format json
reachkit read v2ex hot --limit 5 --format json
reachkit read v2ex topic:1 --limit 5 --format json
reachkit read podcast https://example.com/feed.xml --limit 5 --format json
reachkit read linkedin https://www.linkedin.com/company/example/ --format json
reachkit read xueqiu SH600000 --format json
reachkit read xueqiu hot --limit 5 --format json
reachkit search xueqiu "bank" --limit 5 --format json
reachkit read facebook page_id --format json
reachkit read instagram instagram_user_id --format json
```

Read a URL with an explicit cookie file:

```bash
reachkit read url https://example.com --cookie-file cookies.json --format json
```

Read a URL with an explicit Playwright storage state file:

```bash
reachkit read url https://example.com --storage-state storage-state.json --format json
```

Read rendered page text with the optional browser extra:

```bash
reachkit read browser https://example.com --storage-state storage-state.json --format json
```

Check local readiness:

```bash
reachkit doctor
```

Remove local setup files while keeping user config:

```bash
reachkit setup remove
reachkit setup remove --purge
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

- `source`: `web`, `rss`, `github`, `youtube`, `x`, `xiaohongshu`, or `bilibili`.
- Newer platform readers use the same shape for `reddit`, `v2ex`, `podcast`, `linkedin`, `xueqiu`, `facebook`, and `instagram`.
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

- `web_read`: `url`, optional `max_chars`, optional `cookie_file`, optional `storage_state`.
- `web_search`: `query`, optional `limit`.
- `rss_read`: `url`, optional `limit`.
- `github_read`: `repo`, optional `path`, optional `ref`.
- `github_search`: `query`, optional `limit`.
- `youtube_transcript`: `video`, optional `lang`, optional `max_chars`.
- `youtube_metadata`: `video`.
- `youtube_search`: `query`, optional `limit`.
- `x_read`: `post`.
- `x_search`: `query`, optional `limit`.
- `xiaohongshu_api`: `path`, optional `query` object.
- `xiaohongshu_read`: `path`, optional `query` object.
- `bilibili_read`: `video`.
- `bilibili_search`: `query`, optional `limit`.
- `reddit_read`: `target`, optional `limit`.
- `reddit_search`: `query`, optional `limit`.
- `v2ex_read`: `target`, optional `limit`.
- `podcast_read`: `url`, optional `limit`.
- `xueqiu_quote`: `symbol`.
- `xueqiu_hot`: optional `limit`.
- `browser_read`: `url`, optional `storage_state`, optional `wait_until`, optional `max_chars`.
- `channels_list`: no arguments.
- `channels_doctor`: optional `channel`.
- `auth_status`: no arguments.
- `setup_plan`: no arguments.

See `examples/stdio-request.jsonl` for a small request set.

## Platform access

ReachKit uses public GitHub REST endpoints. You can run without a token, but GitHub rate limits unauthenticated requests more aggressively. To raise the limit, set `GITHUB_TOKEN`.

X post reading uses the official API and requires `X_BEARER_TOKEN` or `TWITTER_BEARER_TOKEN`.

Xiaohongshu reading uses open API paths and requires `XHS_APP_KEY` and `XHS_APP_SECRET`.

On PowerShell, set credentials before running the command:

```powershell
$env:X_BEARER_TOKEN = "your_token_here"
$env:XHS_APP_KEY = "your_key"
$env:XHS_APP_SECRET = "your_secret"
```

On macOS or Linux shells:

```bash
export X_BEARER_TOKEN=your_token_here
export XHS_APP_KEY=your_key
export XHS_APP_SECRET=your_secret
```

YouTube transcript reading uses public timed text when a transcript track is available. YouTube search requires `YOUTUBE_API_KEY`.

Web search requires `REACHKIT_WEB_SEARCH_URL`, which should point to a JSON endpoint that accepts `q` and `limit` query parameters. YouTube metadata uses the same `YOUTUBE_API_KEY` setting as YouTube search.

Bilibili video reading and search fetch public metadata when the public endpoints are reachable.

Reddit, V2EX, podcast, LinkedIn public page, and many Xueqiu reads use public endpoints. Some Xueqiu pages may require an explicit cookie file supplied by the user.

Facebook and Instagram use Graph API paths and require explicit tokens:

```powershell
$env:FACEBOOK_ACCESS_TOKEN = "your_token_here"
$env:INSTAGRAM_ACCESS_TOKEN = "your_token_here"
```

ReachKit config stores environment variable names and explicit file paths:

```bash
reachkit auth set github --token-env GITHUB_TOKEN
reachkit auth set browser --storage-state storage-state.json
reachkit auth set web --cookie-file cookies.json
```

Token values are read from the environment at runtime and are not written to `~/.reachkit/config.toml` by default.

URL reads can use explicit cookie input with `--cookie-file` or `--storage-state`. ReachKit reads JSON cookie lists, Netscape cookie files, and Playwright storage state files supplied by the user. These files are never required for public URL reads and should stay out of Git.

Rendered page reads use the optional browser extra. They can use an explicit storage state file for pages the user can access, but ReachKit does not extract browser profile data.

## Limits and behavior

- `--format` supports `text` and `json`.
- `--max-chars` defaults to `12000` and accepts values from `1` to `100000`.
- `--limit` defaults to `10` and caps at `50`.
- HTTP uses `http://` and `https://` only.
- Cookie and storage state files must be supplied explicitly. ReachKit does not read browser profile storage.
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

No. ReachKit is a focused public content reader. It handles single URLs, feeds, GitHub repository metadata, GitHub text files, GitHub repository search, YouTube transcripts, X posts, Xiaohongshu open API JSON, and Bilibili video metadata. It does not crawl whole sites, render JavaScript, or operate platform bypass flows.

### How is ReachKit different from hosted web search APIs?

Hosted search and extraction APIs are useful when you need ranking, scale, managed crawling, JavaScript rendering, or cited research. ReachKit is for the lighter local path: predictable CLI commands, stdio integration, no mandatory paid API, and outputs that are easy to test.

### Can ReachKit feed a RAG pipeline?

Yes, for public pages, feeds, and GitHub resources. ReachKit can turn those inputs into normalized text records that a RAG ingestion script can chunk, embed, store, or score.

### What searches should find this project?

ReachKit is meant for searches like "Python CLI for AI agent web retrieval", "AI agent tool for reading public URLs", "RSS to JSON command line tool", "GitHub repository search CLI JSON", "YouTube transcript CLI JSON", "X API post reader Python", "Xiaohongshu open API Python", "Bilibili video metadata CLI", "stdio tools/list tools/call Python server", "public web page to clean text Python", and "GitHub README reader for AI agents".

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
