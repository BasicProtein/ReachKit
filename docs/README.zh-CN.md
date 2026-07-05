# ReachKit

<p align="center">
  <a href="README.zh-CN.md"><img alt="中文" src="https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87-2f81f7?style=flat-square"></a>
  <a href="../README.md"><img alt="English" src="https://img.shields.io/badge/README-English-2f81f7?style=flat-square"></a>
  <a href="README.ja.md"><img alt="日本語" src="https://img.shields.io/badge/README-%E6%97%A5%E6%9C%AC%E8%AA%9E-2f81f7?style=flat-square"></a>
  <a href="README.ko.md"><img alt="한국어" src="https://img.shields.io/badge/README-%ED%95%9C%EA%B5%AD%EC%96%B4-2f81f7?style=flat-square"></a>
</p>

ReachKit 给 AI agent 提供一层干净的互联网输入能力：读取网页和 feed、检查 GitHub、拉取字幕和元数据、搜索支持的平台，并返回 agent 真正能使用的小型 JSON 记录。

agent 擅长推理，但很容易卡在获取上下文这一步。原始网页噪声很大，平台 API 可能缺 token，视频不一定公开字幕，临时脚本也可能把日志混进 JSON。ReachKit 把这些边缘问题整理成可预测的 CLI 命令、stdio 工具、provider 诊断和显式 setup 指引。

它适合需要读取公共内容或显式授权内容的工作流，不做隐藏浏览器状态提取、登录自动化、爬虫集群、代理机制或静默凭据收集。给它一个 URL、feed、仓库、文件路径、平台查询、post id、股票代码、播客 feed，或授权 API 目标，ReachKit 会返回字段稳定的标准化文本记录，方便 agent 检查、引用、存储、排序，或传给下一步工具。

## 为什么 agent 需要它

AI agent 不只会因为模型能力不够而失败，也会因为输入层不可靠而失败：

- 搜索结果告诉你页面存在，但 agent 仍然需要正文才能推理。
- feed、GitHub 响应、字幕和社交平台 post 都有不同结构。
- 缺 token 或依赖时，如果到执行中途才发现，整次运行就会被浪费。
- 对简单公共内容来说，浏览器自动化太重，HTTP、解析和干净输出就够了。
- shell 片段很难串联，因为警告、日志和数据经常混在 stdout。
- 凭据处理很敏感，工具不应该静默读取浏览器 profile 或保存 token 值。

ReachKit 处理推理之前的输入步骤：获取、标准化、报告警告，并告诉 agent 哪些能力已经就绪。

## 它适合放在哪里

当你想要一个本地、可检查的检索层，而不是托管爬虫或一堆临时脚本时，可以用 ReachKit：

- 你已经知道一个 URL、feed、仓库、视频、post、股票代码或平台查询。
- 你需要稳定 JSON，用于 agent loop、RAG 入库、CI 检查或监控任务。
- 你希望网页、feed、GitHub、字幕、post 和平台搜索使用同一种结果结构。
- 你需要 `doctor` 告诉你哪里能用、哪里缺配置、下一步怎么修。
- 你偏好显式环境变量和用户提供的文件，而不是隐藏 session 读取。
- 你希望先走简单路径，只在明确需要时再启用渲染页面读取。

ReachKit 不负责给整个互联网排序。它负责把已知的公共内容或显式授权内容变成 agent 可以信任的记录。

## 五分钟能做什么

```bash
reachkit setup plan
reachkit channels doctor
reachkit read url https://example.com --format json
reachkit read github owner/repo --path README.md --format json
reachkit serve stdio
```

这会给 agent 一个快速 readiness map、网页读取器、GitHub 读取器和 stdio 工具服务，而且不需要为每个平台学习一套新 schema。

## 功能

| 用户痛点 | ReachKit 路径 |
| --- | --- |
| “agent 有 URL，但需要可用正文。” | `reachkit read url`、RSS、播客 feed 和可选渲染页面读取。 |
| “agent 需要代码和项目上下文。” | GitHub 仓库、文件、仓库搜索、issue、pull request 和 release 读取。 |
| “agent 需要同一结构的平台内容。” | YouTube、X、小红书、Bilibili、Reddit、V2EX、LinkedIn、雪球、Facebook 和 Instagram 读取/搜索。 |
| “运行失败是因为 setup 缺东西。” | `setup plan`、`channels doctor`、`auth status` 和修复建议。 |
| “agent runtime 要工具，不要自然语言说明。” | `reachkit serve stdio`，支持 `tools/list` 和 `tools/call`。 |
| “凭据必须显式且可控。” | 配置只保存环境变量名和用户提供的文件路径，不保存 token 值。 |

ReachKit 目前提供：

- setup plan/install/update/remove，支持 dry-run 和 safe 模式。
- channels list/doctor，用来查看平台能力、provider 状态、缺失配置和修复建议。
- auth status/set，本地配置只保存环境变量名和显式文件路径，不默认保存 token 明文。
- 读取公共 URL，处理 `text/html`、`text/plain` 和其他可读的 `text/*` 响应。
- URL 读取可显式传入 cookie 输入，支持用户提供的 JSON cookie list、Netscape cookie file 或 Playwright storage state file。
- 使用 Python 标准库提取 HTML 标题并清理正文文本。
- 解析 RSS 和 Atom feed，并输出标准化条目元数据。
- 读取 GitHub 仓库元数据、文件、仓库搜索、issues、pull requests 和 releases。
- 读取公开可用的 YouTube timed text 字幕，并用显式 API key 读取 YouTube 元数据和搜索 YouTube。
- 通过官方 API 读取 X post、搜索、conversation 查询和 timeline-style 查询，需要 `X_BEARER_TOKEN` 或 `TWITTER_BEARER_TOKEN`。
- 通过小红书开放平台读取授权 API JSON、笔记搜索、笔记详情和评论，需要 `XHS_APP_KEY` 和 `XHS_APP_SECRET`。
- 读取 Bilibili 公开视频元数据并搜索公开视频。
- 读取 Reddit 公开搜索、帖子和评论 JSON。
- 读取 V2EX 热门主题、节点主题、带回复的主题详情和用户记录。
- 读取播客 RSS 元数据和 episode 记录。
- 读取 LinkedIn 公开页面文本。
- 读取雪球行情、股票搜索和热门记录。
- 在用户显式提供 token 时读取 Facebook 和 Instagram Graph API 记录。
- 通过可选 `reachkit[browser]` 读取用户有权访问的渲染后页面文本。
- 面向 agent 工具集成的 newline-delimited JSON stdio server。
- 内容命令可输出 text 或 JSON。

ReachKit 不是完整网页爬虫。它不读取浏览器 profile，不处理验证码或访问挑战，不运行代理池，不伪装指纹，也不静默收集登录状态。需要授权的平台必须由用户显式提供环境变量、cookie 文件、storage-state 文件或官方 API token。

## 适合的场景

ReachKit 适合用于：

- 需要公共网页正文，而不是只要搜索摘要的 AI agent 工具。
- 先收集材料，再做摘要、比较或观点核查的研究助手。
- 在 chunk 和 embedding 前需要稳定记录的 RAG 入库脚本。
- 检查 README、文档页、release、issue 和仓库的开发者 agent。
- 监控 feed、changelog、公共文档或平台记录的任务。
- stdout 必须保持可解析的本地命令行管道。
- 偏好 request/response 工具，而不是手写 shell 片段的 agent runtime。
- 需要平台特定内容，但不想为每个平台写一套 schema 的工作流。

如果你需要读取自己有权访问的 JavaScript 渲染页面，可以使用可选 browser extra。如果你需要大规模爬取、访问挑战处理、代理池或反滥用平台处理，ReachKit 不应该位于那一层。

## 安装

ReachKit 需要 Python 3.11 或更高版本。

本地开发：

```bash
python -m pip install -e .
```

使用 `uv` 可以把运行环境隔离开：

```bash
uv venv .venv --python 3.11
uv pip install --python .venv/Scripts/python.exe -e . pytest
```

macOS 或 Linux 下，虚拟环境 Python 通常位于 `.venv/bin/python`。

读取渲染页面时，需要安装可选 browser extra 和浏览器 runtime：

```bash
python -m pip install -e ".[browser]"
python -m playwright install chromium
```

## 快速开始

先查看本地 setup 计划：

```bash
reachkit setup plan
reachkit setup install --dry-run
reachkit setup install --safe
```

创建默认本地配置：

```bash
reachkit setup install
```

检查平台和授权状态：

```bash
reachkit channels list
reachkit channels doctor
reachkit auth status
```

读取公共网页：

```bash
reachkit read url https://example.com --format json
```

读取 feed：

```bash
reachkit read rss https://example.com/feed.xml --limit 5 --format json
```

读取 GitHub 仓库元数据：

```bash
reachkit read github owner/repo --format json
```

读取 GitHub 仓库中的公共文本文件：

```bash
reachkit read github owner/repo --path README.md --ref main --format json
```

搜索公开 GitHub 仓库：

```bash
reachkit search github "agent tools" --limit 5 --format json
```

搜索已配置的 Web endpoint：

```bash
reachkit search web "agent tools" --limit 5 --format json
```

读取 GitHub issue、pull request 和 release：

```bash
reachkit read github owner/repo --issue 7 --format json
reachkit read github owner/repo --pull-request 3 --format json
reachkit read github owner/repo --release v1.0.0 --format json
```

读取公开视频的 YouTube 字幕：

```bash
reachkit read youtube dQw4w9WgXcQ --lang en --format json
reachkit read youtube dQw4w9WgXcQ --metadata --format json
```

使用显式 API key 搜索 YouTube：

```bash
reachkit search youtube "agent tools" --limit 5 --format json
```

通过官方 API 读取 X post：

```bash
reachkit read x 1234567890 --format json
```

通过官方 API 搜索 X：

```bash
reachkit search x "agent tools" --limit 5 --format json
```

使用已配置的 app credentials 读取小红书开放平台 JSON：

```bash
reachkit read xiaohongshu /api/open/path --param note_id=abc --format json
```

通过 BV id 或 av id 读取 Bilibili 公开视频元数据：

```bash
reachkit read bilibili BV1xx411c7mD --format json
reachkit read bilibili av123456 --format json
```

搜索 Bilibili：

```bash
reachkit search bilibili "agent tools" --limit 5 --format json
```

读取其他公共或显式 token 平台：

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

使用显式 cookie 文件读取 URL：

```bash
reachkit read url https://example.com --cookie-file cookies.json --format json
```

使用显式 Playwright storage state 文件读取 URL：

```bash
reachkit read url https://example.com --storage-state storage-state.json --format json
```

使用可选 browser extra 读取渲染页面文本：

```bash
reachkit read browser https://example.com --storage-state storage-state.json --format json
```

检查本地环境：

```bash
reachkit doctor
```

启动 stdio 工具服务：

```bash
reachkit serve stdio
```

## 输出契约

内容命令默认输出纯文本。加上 `--format json` 后会得到稳定对象：

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

每个内容结果都包含：

- `source`：`web`、`rss`、`github`、`youtube`、`x`、`xiaohongshu`、`bilibili`、`reddit`、`v2ex`、`podcast`、`linkedin`、`xueqiu`、`facebook` 或 `instagram`。
- `url`：请求 URL，或可用时的规范结果 URL。
- `title`：网页、feed、仓库、搜索或文件标题。
- `content_type`：可用时的 HTTP content type。
- `items`：标准化文本记录。
- `warnings`：非致命问题，例如 `empty_feed` 或 `non_html_text`。

这个结构刻意保持很小。agent 不需要为每个平台学习一套新 schema。

## Stdio 集成

`reachkit serve stdio` 从 stdin 每行读取一个 JSON 对象，并向 stdout 每行写出一个 JSON 对象。

列出工具：

```json
{"id":"1","method":"tools/list","params":{}}
```

调用工具：

```json
{"id":"2","method":"tools/call","params":{"name":"web_read","arguments":{"url":"https://example.com","max_chars":2000}}}
```

可用工具：

- `web_read`：`url`，可选 `max_chars`，可选 `cookie_file`，可选 `storage_state`。
- `web_search`：`query`，可选 `limit`。
- `rss_read`：`url`，可选 `limit`。
- `github_read`：`repo`，可选 `path`，可选 `ref`。
- `github_search`：`query`，可选 `limit`。
- `youtube_transcript`：`video`，可选 `lang`，可选 `max_chars`。
- `youtube_metadata`：`video`。
- `youtube_search`：`query`，可选 `limit`。
- `x_read`：`post`。
- `x_search`：`query`，可选 `limit`。
- `xiaohongshu_api`：`path`，可选 `query` object。
- `xiaohongshu_read`：`path`，可选 `query` object。
- `bilibili_read`：`video`。
- `bilibili_search`：`query`，可选 `limit`。
- `reddit_read`：`target`，可选 `limit`。
- `reddit_search`：`query`，可选 `limit`。
- `v2ex_read`：`target`，可选 `limit`。
- `podcast_read`：`url`，可选 `limit`。
- `xueqiu_quote`：`symbol`。
- `xueqiu_hot`：可选 `limit`。
- `browser_read`：`url`，可选 `storage_state`，可选 `wait_until`，可选 `max_chars`。
- `channels_list`：无参数。
- `channels_doctor`：可选 `channel`。
- `auth_status`：无参数。
- `setup_plan`：无参数。

`examples/stdio-request.jsonl` 里有一组小型请求样例。

## 平台访问

ReachKit 使用公开 GitHub REST endpoint。没有 token 也能运行，但 GitHub 会对未认证请求设置更严格的 rate limit。设置 `GITHUB_TOKEN` 可以提高限制。

X post 读取使用官方 API，需要 `X_BEARER_TOKEN` 或 `TWITTER_BEARER_TOKEN`。

小红书读取使用开放平台 API path，需要 `XHS_APP_KEY` 和 `XHS_APP_SECRET`。

PowerShell 中先设置凭据：

```powershell
$env:X_BEARER_TOKEN = "your_token_here"
$env:XHS_APP_KEY = "your_key"
$env:XHS_APP_SECRET = "your_secret"
```

macOS 或 Linux shell 中：

```bash
export X_BEARER_TOKEN=your_token_here
export XHS_APP_KEY=your_key
export XHS_APP_SECRET=your_secret
```

YouTube 字幕读取使用公开视频公开 timed text。有些视频不会公开字幕轨道。YouTube 搜索需要 `YOUTUBE_API_KEY`。

Web 搜索需要 `REACHKIT_WEB_SEARCH_URL`，它应指向一个接受 `q` 和 `limit` query 参数的 JSON endpoint。YouTube 元数据读取与 YouTube 搜索使用同一个 `YOUTUBE_API_KEY` 设置。

Bilibili 视频读取和搜索使用可访问的公开元数据路径。

Reddit、V2EX、播客、LinkedIn 公开页面和许多雪球读取使用公开路径。部分雪球页面可能需要用户显式提供 cookie 文件。

Facebook 和 Instagram 使用 Graph API，需要显式 token：

```powershell
$env:FACEBOOK_ACCESS_TOKEN = "your_token_here"
$env:INSTAGRAM_ACCESS_TOKEN = "your_token_here"
```

ReachKit 配置只保存环境变量名和显式文件路径：

```bash
reachkit auth set github --token-env GITHUB_TOKEN
reachkit auth set browser --storage-state storage-state.json
reachkit auth set web --cookie-file cookies.json
```

token 值在运行时从环境变量读取，默认不会写入 `~/.reachkit/config.toml`。

URL 读取可以用 `--cookie-file` 或 `--storage-state` 显式传入 cookie 输入。ReachKit 读取用户提供的 JSON cookie list、Netscape cookie file 或 Playwright storage state file。这类文件不应该提交到 Git。

渲染页面读取使用可选 browser extra。它可以读取用户显式提供的 storage state 文件，用于用户有权访问的页面，但 ReachKit 不提取浏览器 profile 数据。

## 限制与行为

- `--format` 支持 `text` 和 `json`。
- `--max-chars` 默认值是 `12000`，可接受 `1` 到 `100000`。
- `--limit` 默认值是 `10`，最高 `50`。
- HTTP 只接受 `http://` 和 `https://`。
- cookie 或 storage state 文件必须由用户显式提供。ReachKit 不读取浏览器 profile storage。
- 默认 HTTP timeout 是 `15` 秒。
- 响应过大、非 2xx 响应、无效 XML、无效输入和 GitHub 二进制文件都会返回面向用户的错误。
- 只有必需检查失败时，`doctor` 才返回 exit code `1`。

## 为什么不用浏览器

页面需要 JavaScript、认证或交互时，浏览器很有用。但浏览器也更慢，更难沙箱化，也更难做到确定性输出。

ReachKit 优先处理公共内容路径：fetch、parse、normalize，然后返回一个小记录。这让它更容易测试，也更容易放进 agent loop。

## 常见问题

### ReachKit 是什么？

ReachKit 是一个本地检索工具包，面向 AI agent。它读取公共 URL、RSS 或 Atom feed，以及 GitHub 资源，然后以纯文本或 JSON 返回干净文本记录。

### ReachKit 解决 agent 的什么问题？

agent 经常需要新鲜的公共上下文，但原始网页、feed XML 和 GitHub API payload 都不好直接传来传去。ReachKit 提供一个小契约：获取内容、清理文本、保留有用元数据，并把警告单独报告。

### ReachKit 是网页爬虫吗？

不是。ReachKit 是聚焦的公共内容读取器。它处理单个 URL、feed、GitHub 仓库元数据、GitHub 文本文件和 GitHub 仓库搜索。它不会爬完整站点、渲染 JavaScript，也不处理登录内容。

### ReachKit 和托管 Web Search API 有什么区别？

如果你需要排序、规模化抓取、托管爬取、JavaScript 渲染或带引用的研究，托管搜索和抽取 API 很有价值。ReachKit 走的是更轻的本地路径：可预测的 CLI 命令、stdio 集成、非强制付费 API，以及容易测试的输出。

### ReachKit 可以给 RAG pipeline 供料吗？

可以，适用于公共网页、feed 和 GitHub 资源。ReachKit 可以把这些输入转成标准化文本记录，后续脚本再进行 chunk、embedding、存储或打分。

### 哪些搜索词应该能找到这个项目？

ReachKit 面向这些搜索需求："Python CLI for AI agent web retrieval"、"AI agent tool for reading public URLs"、"RSS to JSON command line tool"、"GitHub repository search CLI JSON"、"stdio tools/list tools/call Python server"、"public web page to clean text Python"、"GitHub README reader for AI agents"。

## 开发

运行测试：

```bash
python -m pytest -q
```

运行 smoke check：

```bash
reachkit doctor
reachkit read url https://example.com --format json
```

测试套件尽量使用 fixture 和 mocked HTTP 路径，因此常规测试不依赖实时网站。

## License

Apache-2.0. See `LICENSE`.
