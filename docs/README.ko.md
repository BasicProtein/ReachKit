# ReachKit

<p align="center">
  <a href="README.zh-CN.md"><img alt="中文" src="https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87-2f81f7?style=flat-square"></a>
  <a href="../README.md"><img alt="English" src="https://img.shields.io/badge/README-English-2f81f7?style=flat-square"></a>
  <a href="README.ja.md"><img alt="日本語" src="https://img.shields.io/badge/README-%E6%97%A5%E6%9C%AC%E8%AA%9E-2f81f7?style=flat-square"></a>
  <a href="README.ko.md"><img alt="한국어" src="https://img.shields.io/badge/README-%ED%95%9C%EA%B5%AD%EC%96%B4-2f81f7?style=flat-square"></a>
</p>

ReachKit은 AI agent를 위한 깨끗한 internet intake layer입니다. web pages와 feeds를 읽고, GitHub를 살펴보고, transcripts와 metadata를 가져오고, 지원되는 platform을 검색한 뒤 agent가 바로 사용할 수 있는 작은 JSON records를 반환합니다.

agent는 reasoning에는 강하지만 retrieval에서는 쉽게 깨집니다. raw webpage는 noise가 많고, platform API에는 token이 필요할 수 있고, video transcript는 public timed text가 있을 때만 사용할 수 있습니다. 작은 script도 JSON에 log가 섞이면 tool chain에서 다루기 어렵습니다. ReachKit은 이런 가장자리 문제를 predictable CLI commands, stdio tools, provider diagnostics, explicit setup guidance로 정리합니다.

공개 content 또는 명시적으로 authorization된 content가 필요한 workflow를 위한 도구입니다. hidden browser extraction, login automation, crawler farms, proxy machinery, silent credential collection은 하지 않습니다. URL, feed, repository, file path, platform query, post id, stock symbol, podcast feed, authorized API target을 넘기면 ReachKit은 안정적인 fields를 가진 normalized text records를 반환합니다.

## Agent에게 왜 필요한가

AI agent는 model이 약해서만 실패하지 않습니다. input layer가 불안정해도 실패합니다.

- 검색 결과는 page가 있다는 사실만 알려 주고, reasoning에는 page body가 필요합니다.
- feed, GitHub response, transcript, social post는 모두 다른 shape로 옵니다.
- token이나 dependency 누락을 실행 중간에 발견하면 run 전체가 낭비됩니다.
- 단순한 public content에는 browser automation이 무겁고, HTTP, parsing, clean output이면 충분합니다.
- shell snippet은 warning, log, data가 stdout에 섞일 때 chain하기 어렵습니다.
- credential handling은 조심해야 하며, tool이 browser profile을 몰래 읽거나 token value를 저장하면 안 됩니다.

ReachKit은 reasoning 전에 input step을 처리합니다. fetch, normalize, warn을 수행하고 agent에게 무엇이 ready인지 알려 줍니다.

## 어디에 맞는가

hosted crawler나 임시 script 묶음이 아니라, local이고 inspectable한 retrieval layer가 필요할 때 ReachKit이 맞습니다.

- URL, feed, repository, video, post, stock symbol, platform query를 이미 알고 있다.
- agent loop, RAG ingestion, CI check, monitoring job에 stable JSON이 필요하다.
- web page, feed, GitHub, transcript, post, platform search를 같은 result shape로 다루고 싶다.
- `doctor`가 무엇이 동작하고, 무엇에 config가 필요하며, 다음에 무엇을 해야 하는지 알려 주길 원한다.
- hidden session reading 대신 explicit environment variables와 user-supplied files를 선호한다.
- 먼저 simple path를 쓰고, 필요할 때만 rendered-page reads를 선택하고 싶다.

ReachKit은 전체 internet을 ranking하는 도구가 아닙니다. 이미 알고 있는 public source나 명시적으로 authorized된 source를 agent가 믿고 쓸 수 있는 records로 바꿉니다.

## 5분 안에 할 수 있는 것

```bash
reachkit setup plan
reachkit channels doctor
reachkit read url https://example.com --format json
reachkit read github owner/repo --path README.md --format json
reachkit serve stdio
```

이렇게 하면 agent는 readiness map, web reader, GitHub reader, stdio tool server를 얻습니다. source마다 새 schema를 배울 필요도 없습니다.

## 기능

| User pain | ReachKit path |
| --- | --- |
| "agent가 URL은 있지만 usable text가 필요하다." | `reachkit read url`, RSS, podcast feed, optional rendered-page readers. |
| "agent에게 code와 project context가 필요하다." | GitHub repo, file, repository search, issue, pull request, release readers. |
| "platform content를 같은 shape로 다루고 싶다." | YouTube, X, Xiaohongshu, Bilibili, Reddit, V2EX, LinkedIn, Xueqiu, Facebook, Instagram readers/searchers. |
| "setup 누락 때문에 run이 실패한다." | `setup plan`, `channels doctor`, `auth status`, fix messages. |
| "agent runtime은 prose가 아니라 tool을 원한다." | `reachkit serve stdio` with `tools/list` and `tools/call`. |
| "credentials는 명시적으로 다뤄야 한다." | config는 env var names와 user-supplied file paths만 저장하고 token values는 저장하지 않습니다. |

ReachKit은 현재 다음을 제공합니다.

- setup plan/install/update/remove. dry-run 및 safe mode를 지원합니다.
- channels list/doctor로 platform capability, provider readiness, missing config, fix guidance 확인.
- auth status/set. local config에는 env var 이름과 명시적 file path만 저장하며 token value는 기본적으로 저장하지 않습니다.
- `text/html`, `text/plain`, 기타 읽을 수 있는 `text/*` response를 가진 public URL 읽기.
- URL reads에서 사용자가 명시적으로 제공한 JSON cookie list, Netscape cookie file, Playwright storage state file을 사용할 수 있습니다.
- Python standard library를 사용한 HTML title extraction과 readable text cleanup.
- RSS 및 Atom feed parsing과 normalized entry metadata.
- GitHub repository metadata, file reading, repository search, issues, pull requests, releases.
- public timed text가 있는 YouTube transcript 및 명시적 API key를 쓰는 YouTube metadata/search.
- official API를 통한 X post, search, conversation query, timeline-style query. `X_BEARER_TOKEN` 또는 `TWITTER_BEARER_TOKEN`이 필요합니다.
- Xiaohongshu open API JSON, note search, note detail, comments. `XHS_APP_KEY`와 `XHS_APP_SECRET`이 필요합니다.
- Bilibili public video metadata 및 public video search.
- Reddit public search, posts, comments.
- V2EX hot topics, node topics, replies를 포함한 topic detail, user records.
- podcast RSS metadata 및 episode records.
- LinkedIn public page text.
- Xueqiu quote, stock search, hot records.
- 명시적 token을 쓰는 Facebook / Instagram Graph API records.
- optional `reachkit[browser]`를 통한, 사용자가 access할 수 있는 rendered page text 읽기.
- agent tool integration을 위한 newline-delimited JSON stdio server.
- content commands의 text 및 JSON output.

ReachKit은 full web crawler가 아닙니다. browser profile을 읽지 않고, access challenge를 처리하지 않고, proxy pool을 운영하지 않고, fingerprint spoofing을 하지 않으며, login state를 조용히 수집하지 않습니다. 인증이 필요한 path는 사용자가 env var, cookie file, storage-state file, official API token을 명시적으로 제공해야 합니다.

## 잘 맞는 사용처

ReachKit은 다음을 만들 때 유용합니다.

- thin snippets가 아니라 public web page body가 필요한 AI agent tools.
- sources를 모은 뒤 summarization, comparison, claim checking을 하는 research assistants.
- chunking과 embedding 전에 stable records가 필요한 RAG ingestion scripts.
- README, docs, releases, issues, repositories를 살피는 developer agents.
- feeds, changelogs, public docs, platform records를 monitoring하는 jobs.
- stdout을 parseable하게 유지해야 하는 local CLI pipelines.
- handwritten shell snippets보다 request/response tools를 선호하는 agent runtimes.
- platform-specific content가 필요하지만 platform마다 schema를 새로 만들고 싶지 않은 workflows.

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

local setup plan 확인:

```bash
reachkit setup plan
reachkit setup install --dry-run
reachkit setup install --safe
```

platform 및 auth status 확인:

```bash
reachkit channels list
reachkit channels doctor
reachkit auth status
```

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

configured web endpoint 검색:

```bash
reachkit search web "agent tools" --limit 5 --format json
```

GitHub issue, pull request, release 읽기:

```bash
reachkit read github owner/repo --issue 7 --format json
reachkit read github owner/repo --pull-request 3 --format json
reachkit read github owner/repo --release v1.0.0 --format json
```

public timed text가 있는 YouTube transcript 읽기:

```bash
reachkit read youtube dQw4w9WgXcQ --lang en --format json
reachkit read youtube dQw4w9WgXcQ --metadata --format json
```

YouTube 검색:

```bash
reachkit search youtube "agent tools" --limit 5 --format json
```

official API로 X post 읽기:

```bash
reachkit read x 1234567890 --format json
```

official API로 X 검색:

```bash
reachkit search x "agent tools" --limit 5 --format json
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

다른 source 읽기:

```bash
reachkit search bilibili "agent tools" --limit 5 --format json
reachkit read reddit https://www.reddit.com/r/example/comments/abc/title/ --format json
reachkit read v2ex hot --limit 5 --format json
reachkit read v2ex topic:1 --limit 5 --format json
reachkit read podcast https://example.com/feed.xml --limit 5 --format json
reachkit read linkedin https://www.linkedin.com/company/example/ --format json
reachkit read xueqiu SH600000 --format json
reachkit read xueqiu hot --limit 5 --format json
reachkit read facebook page_id --format json
reachkit read instagram instagram_user_id --format json
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

- `source`: `web`, `rss`, `github`, `youtube`, `x`, `xiaohongshu`, `bilibili`, `reddit`, `v2ex`, `podcast`, `linkedin`, `xueqiu`, `facebook`, `instagram`.
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
- `channels_list`: arguments 없음.
- `channels_doctor`: optional `channel`.
- `auth_status`: arguments 없음.
- `setup_plan`: arguments 없음.

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

YouTube transcript reading은 video가 public timed text track을 제공할 때 사용할 수 있습니다. YouTube search에는 `YOUTUBE_API_KEY`가 필요합니다.

Web search에는 `REACHKIT_WEB_SEARCH_URL`이 필요합니다. 이 값은 `q`와 `limit` query parameter를 받는 JSON endpoint를 가리켜야 합니다. YouTube metadata는 YouTube search와 같은 `YOUTUBE_API_KEY` setting을 사용합니다.

Bilibili video reading/search는 public metadata path가 reachable할 때 사용할 수 있습니다.

Facebook과 Instagram은 Graph API를 사용하며 명시적 token이 필요합니다.

```powershell
$env:FACEBOOK_ACCESS_TOKEN = "your_token_here"
$env:INSTAGRAM_ACCESS_TOKEN = "your_token_here"
```

ReachKit config는 env var 이름과 명시적 file path만 저장합니다.

```bash
reachkit auth set github --token-env GITHUB_TOKEN
reachkit auth set browser --storage-state storage-state.json
reachkit auth set web --cookie-file cookies.json
```

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
