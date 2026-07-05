# ReachKit

<p align="center">
  <a href="README.zh-CN.md"><img alt="中文" src="https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87-2f81f7?style=flat-square"></a>
  <a href="../README.md"><img alt="English" src="https://img.shields.io/badge/README-English-2f81f7?style=flat-square"></a>
  <a href="README.ja.md"><img alt="日本語" src="https://img.shields.io/badge/README-%E6%97%A5%E6%9C%AC%E8%AA%9E-2f81f7?style=flat-square"></a>
  <a href="README.ko.md"><img alt="한국어" src="https://img.shields.io/badge/README-%ED%95%9C%EA%B5%AD%EC%96%B4-2f81f7?style=flat-square"></a>
</p>

ReachKit 是一个面向 AI agent 的 Python CLI 和库，用来稳定读取公共网页、RSS 或 Atom feed，以及 GitHub 内容。

它适合那些不需要浏览器会话、登录流程、爬虫集群或付费搜索栈的 agent 工作流。给它一个公共 URL、feed、仓库、文件路径或 GitHub 搜索查询，ReachKit 会返回字段稳定的标准化文本记录，方便 agent 检查、引用、存储、排序，或传给下一步工具。

## 为什么需要 ReachKit

AI agent 在获取公共上下文时，经常遇到这些问题：

- 搜索摘要太薄，无法支撑推理。agent 需要网页正文、feed 条目、仓库元数据和文件内容，而不只是标题和链接。
- Web 内容形态不统一。HTML、纯文本、RSS、Atom 和 GitHub API payload 都要先解析，agent 才能真正使用。
- 浏览器自动化对简单公共内容来说太重。很多任务只需要 HTTP、文本清理和稳定输出。
- 临时脚本很难串联。有的命令输出自然语言，有的输出半截 JSON，有的把警告混进 stdout。
- agent 工具调用需要契约。一个工具如果有时返回文本、有时崩溃、有时把日志打到结果里，就很难放进链路。
- 公共仓库也是研究材料。agent 常常需要 README、仓库简介、语言、stars、默认分支和 GitHub 搜索结果。
- 本地诊断很重要。缺 GitHub token、HTTPS runtime 异常、控制台不是 UTF-8，都可能浪费一次完整运行。

ReachKit 负责的是一个朴素但关键的层：从“agent 需要公共上下文”到“agent 拿到可推理的干净文本”之间的那段工作。

## 它适合放在哪里

现在有很多成熟的托管 API，可以做网页搜索、站点抓取、JavaScript 渲染、Markdown 提取、排序和托管式研究。ReachKit 处理的是更小、更本地、但仍然需要可靠的任务：

- 你已经知道要读取的公共 URL、feed、仓库或 GitHub 查询。
- 你希望用一个 Python 命令跑在 CI、本地脚本或 agent 沙箱里。
- 你需要 stdout 保持机器可读，方便下一步工具解析。
- 你希望警告和错误显式出现，而不是悄悄丢掉部分结果。
- 你想用同一条路径读取公共网页、feed、GitHub 元数据和 GitHub 文本文件。
- 你需要一个低配置的输入层，用于 RAG、摘要、监控或开发者研究。

简单说，ReachKit 不解决“给整个互联网排序”这个问题。它解决的是把已知公共来源变成 agent 可以信任的干净记录。

## 功能

ReachKit 目前提供：

- 读取公共 URL，处理 `text/html`、`text/plain` 和其他可读的 `text/*` 响应。
- 使用 Python 标准库提取 HTML 标题并清理正文文本。
- 解析 RSS 和 Atom feed，并输出标准化条目元数据。
- 通过公开 GitHub REST API 读取仓库元数据。
- 通过 GitHub contents API 读取仓库文本文件，包括 base64 编码内容。
- 搜索公开 GitHub 仓库，并返回稳定字段。
- `doctor` 命令，用于检查 Python 版本、UTF-8 I/O、HTTPS runtime、GitHub token 和网络状态。
- 面向 agent 工具集成的 newline-delimited JSON stdio server。
- 内容命令可输出 text 或 JSON。

ReachKit 不是完整网页爬虫。它不处理浏览器会话、cookies、登录内容、社交媒体抓取、音频、视频或付费搜索 API。

## 适合的场景

ReachKit 适合用于：

- 需要公共网页正文的 AI agent 工具。
- README、文档页和发布 feed 的检索流程。
- 先读取 RSS 或 Atom feed、再进行摘要的研究助手。
- 面向开发者 agent 的 GitHub 仓库发现工具。
- 需要确定性 JSON 的本地命令行管道。
- 需要 request/response 对象的 stdio agent 工具。
- 面向公共网页和 feed 的轻量 RAG 入库脚本。
- 监控公共文档、changelog、feed 或 GitHub 文件的 CI 检查。
- 不想启动浏览器，但需要网页、feed 和仓库上下文的开发者研究脚本。

如果你需要 JavaScript 渲染、认证站点、大规模爬取或反滥用平台处理，ReachKit 不应该位于那一层。

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

## 快速开始

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

- `source`：`web`、`rss` 或 `github`。
- `url`：请求 URL，或可用时的规范结果 URL。
- `title`：网页、feed、仓库、搜索或文件标题。
- `content_type`：可用时的 HTTP content type。
- `items`：标准化文本记录。
- `warnings`：非致命问题，例如 `empty_feed` 或 `non_html_text`。

这个结构刻意保持很小。agent 不需要为每种来源学习一套新 schema。

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

- `web_read`：`url`，可选 `max_chars`。
- `rss_read`：`url`，可选 `limit`。
- `github_read`：`repo`，可选 `path`，可选 `ref`。
- `github_search`：`query`，可选 `limit`。

`examples/stdio-request.jsonl` 里有一组小型请求样例。

## GitHub 访问

ReachKit 使用公开 GitHub REST endpoint。没有 token 也能运行，但 GitHub 会对未认证请求设置更严格的 rate limit。

如需提高限制，设置：

```bash
GITHUB_TOKEN=your_token_here
```

该 token 只会作为 GitHub API 请求的 HTTP bearer token 使用。

## 限制与行为

- `--format` 支持 `text` 和 `json`。
- `--max-chars` 默认值是 `12000`，可接受 `1` 到 `100000`。
- `--limit` 默认值是 `10`，最高 `50`。
- HTTP 只接受 `http://` 和 `https://`。
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
