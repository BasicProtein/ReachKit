# ReachKit

<p align="center">
  <a href="README.zh-CN.md"><img alt="中文" src="https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87-2f81f7?style=flat-square"></a>
  <a href="../README.md"><img alt="English" src="https://img.shields.io/badge/README-English-2f81f7?style=flat-square"></a>
  <a href="README.ja.md"><img alt="日本語" src="https://img.shields.io/badge/README-%E6%97%A5%E6%9C%AC%E8%AA%9E-2f81f7?style=flat-square"></a>
  <a href="README.ko.md"><img alt="한국어" src="https://img.shields.io/badge/README-%ED%95%9C%EA%B5%AD%EC%96%B4-2f81f7?style=flat-square"></a>
</p>

ReachKit은 AI agent가 공개 웹 페이지, RSS 또는 Atom feed, GitHub 콘텐츠, YouTube transcripts, X posts, Xiaohongshu open API JSON, Bilibili video metadata를 안정적으로 읽을 수 있게 해 주는 Python CLI 및 라이브러리입니다.

브라우저 세션, 로그인 흐름, 크롤러 팜, 유료 검색 스택 없이 retrieval이 필요한 agent workflow를 위해 만들었습니다. 공개 URL, feed, repository, file path, GitHub search query, YouTube video, X post id, Bilibili video id를 넘기면 ReachKit은 안정적인 JSON 필드를 가진 normalized text records를 반환합니다. agent는 이를 확인하고, 인용하고, 저장하고, 순위를 매기거나, 다음 tool에 넘길 수 있습니다.

## ReachKit이 필요한 이유

AI agent는 공개 context를 가져올 때 같은 문제를 반복해서 만납니다.

- 검색 snippet은 reasoning에 너무 얇습니다. agent에는 title과 URL뿐 아니라 page text, feed entries, repository metadata, file contents가 필요합니다.
- Web content의 형태가 제각각입니다. HTML, plain text, RSS, Atom, GitHub API payload는 agent가 쓰기 전에 각각 parsing이 필요합니다.
- 단순한 공개 content에는 browser automation이 무겁습니다. 많은 작업은 HTTP, text cleanup, predictable output만 있으면 됩니다.
- 임시 script는 신뢰하기 어렵습니다. 어떤 command는 prose를 출력하고, 어떤 command는 partial JSON을 출력하며, 어떤 command는 warnings를 stdout에 섞습니다.
- agent tool call에는 contract가 필요합니다. 어떤 때는 text를 반환하고, 어떤 때는 crash하고, 어떤 때는 log를 result에 섞는 tool은 chain에 넣기 어렵습니다.
- 공개 repository도 research material입니다. agent는 README, repository summary, language, stars, default branch, GitHub search results가 필요할 때가 많습니다.
- local diagnostics가 중요합니다. GitHub token 누락, HTTPS runtime 문제, UTF-8이 아닌 console은 한 번의 실행 전체를 낭비하게 만들 수 있습니다.

ReachKit은 "agent가 public context를 필요로 한다"와 "agent가 clean text로 reasoning할 수 있다" 사이의 작지만 중요한 층을 맡습니다.

## 어디에 맞는가

Web search, crawling, JavaScript rendering, Markdown extraction, ranking, managed research를 위한 강력한 hosted API는 이미 많습니다. ReachKit은 더 작고 local에 가까우면서도 신뢰성이 필요한 작업에 맞습니다.

- 읽을 공개 URL, feed, repository, GitHub query를 이미 알고 있다.
- Python command를 CI, local scripts, agent sandbox에서 실행하고 싶다.
- 다음 tool이 parsing할 수 있도록 stdout을 machine-readable하게 유지하고 싶다.
- 조용히 일부만 출력하는 대신, 명시적인 warnings와 typed errors가 필요하다.
- public GitHub metadata와 text files를 web pages, feeds와 같은 retrieval path에서 다루고 싶다.
- RAG, summarization, monitoring, developer research를 위한 low-setup input stage가 필요하다.

간단히 말하면 ReachKit은 전체 web을 ranking하는 도구가 아닙니다. 이미 알고 있는 public sources를 agent가 믿고 쓸 수 있는 clean records로 바꾸는 도구입니다.

## 기능

ReachKit은 현재 다음을 제공합니다.

- `text/html`, `text/plain`, 기타 읽을 수 있는 `text/*` response를 가진 public URL 읽기.
- URL reads에서 사용자가 명시적으로 제공한 JSON cookie list, Netscape cookie file, Playwright storage state file을 사용할 수 있습니다.
- Python standard library를 사용한 HTML title extraction과 readable text cleanup.
- RSS 및 Atom feed parsing과 normalized entry metadata.
- public GitHub REST API를 통한 repository metadata 읽기.
- GitHub contents API를 통한 repository text file 읽기. base64 text file도 처리합니다.
- stable item fields를 가진 public GitHub repository search.
- public timed text가 있는 YouTube transcript 읽기.
- official API를 통한 X post 읽기. `X_BEARER_TOKEN` 또는 `TWITTER_BEARER_TOKEN`이 필요합니다.
- Xiaohongshu open API JSON 읽기. `XHS_APP_KEY`와 `XHS_APP_SECRET`이 필요합니다.
- BV video id에 대한 Bilibili public video metadata 읽기.
- optional `reachkit[browser]`를 통한, 사용자가 access할 수 있는 rendered page text 읽기.
- Python version, UTF-8 I/O, HTTPS runtime, GitHub token, network checks를 위한 `doctor` command.
- agent tool integration을 위한 newline-delimited JSON stdio server.
- content commands의 text 및 JSON output.

ReachKit은 full web crawler가 아닙니다. browser profile을 읽지 않고, access challenge를 처리하지 않고, proxy pool을 운영하지 않으며, login-only page를 다루지 않습니다. URL read에서 cookie를 쓰는 경우는 사용자가 cookie file을 명시적으로 제공할 때뿐입니다.

## 잘 맞는 사용처

ReachKit은 다음을 만들 때 유용합니다.

- public web page text가 필요한 AI agent tools.
- YouTube transcript text, X post text, Xiaohongshu open API JSON, Bilibili video metadata를 다른 source와 같은 JSON shape로 다루는 workflows.
- README files, docs pages, release feeds를 위한 retrieval workflows.
- RSS 또는 Atom feeds를 읽은 뒤 요약하는 research assistants.
- developer agents를 위한 GitHub repository discovery tools.
- deterministic JSON이 필요한 local command-line pipelines.
- request 및 response objects를 기대하는 agent runtimes용 stdio tools.
- public pages와 feeds를 위한 lightweight RAG ingestion scripts.
- public docs, changelogs, feeds, GitHub files를 monitoring하는 CI checks.
- browser 없이 web, feed, repository context가 필요한 developer research scripts.

사용자가 access할 수 있는 JavaScript rendered page를 읽어야 한다면 optional browser extra를 사용할 수 있습니다. large-scale crawling, access challenge handling, proxy pools, anti-abuse platform handling이 필요하다면 ReachKit은 그 층을 담당하지 않습니다.

## 설치

ReachKit은 Python 3.11 이상이 필요합니다.

Local development:

```bash
python -m pip install -e .
```

`uv`를 사용하면 runtime을 분리할 수 있습니다.

```bash
uv venv .venv --python 3.11
uv pip install --python .venv/Scripts/python.exe -e . pytest
```

macOS 또는 Linux에서는 virtual environment Python path가 보통 `.venv/bin/python`입니다.

Rendered page reads에는 optional browser extra와 browser runtime이 필요합니다.

```bash
python -m pip install -e ".[browser]"
python -m playwright install chromium
```

## Quick start

공개 web page 읽기:

```bash
reachkit read url https://example.com --format json
```

feed 읽기:

```bash
reachkit read rss https://example.com/feed.xml --limit 5 --format json
```

GitHub repository metadata 읽기:

```bash
reachkit read github owner/repo --format json
```

GitHub repository의 public text file 읽기:

```bash
reachkit read github owner/repo --path README.md --ref main --format json
```

public GitHub repositories 검색:

```bash
reachkit search github "agent tools" --limit 5 --format json
```

public timed text가 있는 YouTube transcript 읽기:

```bash
reachkit read youtube dQw4w9WgXcQ --lang en --format json
```

official API로 X post 읽기:

```bash
reachkit read x 1234567890 --format json
```

configured app credentials로 Xiaohongshu open API JSON 읽기:

```bash
reachkit read xiaohongshu /api/open/path --param note_id=abc --format json
```

BV id 또는 av id로 Bilibili public video metadata 읽기:

```bash
reachkit read bilibili BV1xx411c7mD --format json
reachkit read bilibili av123456 --format json
```

명시적인 cookie file로 URL 읽기:

```bash
reachkit read url https://example.com --cookie-file cookies.json --format json
```

명시적인 Playwright storage state file로 URL 읽기:

```bash
reachkit read url https://example.com --storage-state storage-state.json --format json
```

optional browser extra로 rendered page text 읽기:

```bash
reachkit read browser https://example.com --storage-state storage-state.json --format json
```

local readiness 확인:

```bash
reachkit doctor
```

stdio tool server 실행:

```bash
reachkit serve stdio
```

## Output contract

Content commands는 기본적으로 plain text를 출력합니다. `--format json`을 추가하면 stable object를 얻습니다.

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

모든 content result는 다음을 가집니다.

- `source`: `web`, `rss`, `github`, `youtube`, `x`, `xiaohongshu`, `bilibili`.
- `url`: request URL 또는 사용 가능한 canonical result URL.
- `title`: page, feed, repository, search, file title.
- `content_type`: 사용 가능한 HTTP content type.
- `items`: normalized text records.
- `warnings`: `empty_feed`, `non_html_text` 같은 non-fatal issues.

이 shape는 일부러 작게 유지됩니다. agent는 source마다 새로운 schema를 배울 필요가 없습니다.

## Stdio integration

`reachkit serve stdio`는 stdin에서 line당 하나의 JSON object를 읽고 stdout에 line당 하나의 JSON object를 씁니다.

Tool list:

```json
{"id":"1","method":"tools/list","params":{}}
```

Tool call:

```json
{"id":"2","method":"tools/call","params":{"name":"web_read","arguments":{"url":"https://example.com","max_chars":2000}}}
```

Available tools:

- `web_read`: `url`, optional `max_chars`, optional `cookie_file`, optional `storage_state`.
- `rss_read`: `url`, optional `limit`.
- `github_read`: `repo`, optional `path`, optional `ref`.
- `github_search`: `query`, optional `limit`.
- `youtube_transcript`: `video`, optional `lang`, optional `max_chars`.
- `x_read`: `post`.
- `xiaohongshu_api`: `path`, optional `query` object.
- `bilibili_read`: `video`.
- `browser_read`: `url`, optional `storage_state`, optional `wait_until`, optional `max_chars`.

작은 request set은 `examples/stdio-request.jsonl`에 있습니다.

## Platform access

ReachKit은 public GitHub REST endpoints를 사용합니다. token 없이도 실행할 수 있지만 GitHub는 unauthenticated requests에 더 엄격한 rate limit을 적용합니다. limit을 높이려면 `GITHUB_TOKEN`을 설정합니다.

X post reading은 official API를 사용하며 `X_BEARER_TOKEN` 또는 `TWITTER_BEARER_TOKEN`이 필요합니다.

Xiaohongshu reading은 open API path를 사용하며 `XHS_APP_KEY`와 `XHS_APP_SECRET`이 필요합니다.

PowerShell에서는 command 실행 전에 credentials를 설정합니다.

```powershell
$env:X_BEARER_TOKEN = "your_token_here"
$env:XHS_APP_KEY = "your_key"
$env:XHS_APP_SECRET = "your_secret"
```

macOS 또는 Linux shell에서는:

```bash
export X_BEARER_TOKEN=your_token_here
export XHS_APP_KEY=your_key
export XHS_APP_SECRET=your_secret
```

YouTube transcript reading은 video가 public timed text track을 제공할 때 사용할 수 있습니다. 모든 video가 public transcript를 제공하지는 않습니다.

Bilibili video reading은 BV id의 public metadata를 가져옵니다.

URL reads는 `--cookie-file` 또는 `--storage-state`로 cookie input을 명시적으로 받을 수 있습니다. ReachKit은 사용자가 제공한 JSON cookie list, Netscape cookie file, Playwright storage state file을 읽습니다. 이런 file은 Git에 들어가면 안 됩니다.

Rendered page reads는 optional browser extra를 사용합니다. 사용자가 access할 수 있는 page에 대해 명시적으로 제공된 storage state file을 사용할 수 있지만, ReachKit은 browser profile data를 추출하지 않습니다.

## Limits and behavior

- `--format`은 `text`와 `json`을 지원합니다.
- `--max-chars` 기본값은 `12000`이고 `1`부터 `100000`까지 받을 수 있습니다.
- `--limit` 기본값은 `10`이고 최대 `50`입니다.
- HTTP는 `http://`와 `https://`만 사용합니다.
- cookie file과 storage state file은 명시적으로 제공되어야 합니다. ReachKit은 browser profile storage를 읽지 않습니다.
- 기본 HTTP timeout은 `15`초입니다.
- 너무 큰 responses, non-2xx responses, invalid XML, invalid input, binary GitHub files는 user-facing errors를 반환합니다.
- `doctor`는 required check가 실패할 때만 exit code `1`을 반환합니다.

## 왜 browser를 쓰지 않는가

page에 JavaScript, authentication, interaction이 필요하면 browser가 유용합니다. 하지만 browser는 더 느리고, sandbox 처리도 어렵고, deterministic output을 만들기도 어렵습니다.

ReachKit은 public-content path를 먼저 처리합니다. fetch, parse, normalize를 거쳐 작은 record를 반환합니다. 그래서 test하기 쉽고 agent loop에 연결하기 쉽습니다.

## 자주 묻는 질문

### ReachKit은 무엇인가요?

ReachKit은 AI agent를 위한 local retrieval toolkit입니다. public URLs, RSS 또는 Atom feeds, GitHub resources를 읽고 clean text records를 plain text 또는 JSON으로 반환합니다.

### ReachKit은 AI agent의 어떤 문제를 해결하나요?

agent는 fresh public context가 필요하지만 raw web pages, feed XML, GitHub API payloads는 그대로 다루기 어렵습니다. ReachKit은 content를 가져오고, text를 정리하고, useful metadata를 유지하고, warnings를 따로 보고하는 작은 contract를 제공합니다.

### ReachKit은 web crawler인가요?

아닙니다. ReachKit은 focused public content reader입니다. single URLs, feeds, GitHub repository metadata, GitHub text files, GitHub repository search를 처리합니다. whole sites를 crawl하거나 JavaScript를 render하거나 login-only content를 다루지 않습니다.

### Hosted web search API와 무엇이 다른가요?

ranking, scale, managed crawling, JavaScript rendering, cited research가 필요하면 hosted search and extraction APIs가 유용합니다. ReachKit은 더 가벼운 local path를 위한 도구입니다. predictable CLI commands, stdio integration, mandatory paid API 없음, test하기 쉬운 outputs를 중시합니다.

### ReachKit을 RAG pipeline에 넣을 수 있나요?

네, public pages, feeds, GitHub resources에 사용할 수 있습니다. ReachKit은 이 input들을 normalized text records로 바꾸고, RAG ingestion script가 chunk, embed, store, score할 수 있게 합니다.

### 어떤 검색어로 이 project를 찾을 수 있어야 하나요?

ReachKit은 "Python CLI for AI agent web retrieval", "AI agent tool for reading public URLs", "RSS to JSON command line tool", "GitHub repository search CLI JSON", "stdio tools/list tools/call Python server", "public web page to clean text Python", "GitHub README reader for AI agents" 같은 검색에 맞습니다.

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

Test suite는 가능한 곳에서 fixtures와 mocked HTTP paths를 사용하므로 일반 테스트는 live websites에 의존하지 않습니다.

## License

Apache-2.0. See `LICENSE`.
