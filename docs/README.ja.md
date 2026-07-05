# ReachKit

<p align="center">
  <a href="README.zh-CN.md"><img alt="中文" src="https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87-2f81f7?style=flat-square"></a>
  <a href="../README.md"><img alt="English" src="https://img.shields.io/badge/README-English-2f81f7?style=flat-square"></a>
  <a href="README.ja.md"><img alt="日本語" src="https://img.shields.io/badge/README-%E6%97%A5%E6%9C%AC%E8%AA%9E-2f81f7?style=flat-square"></a>
  <a href="README.ko.md"><img alt="한국어" src="https://img.shields.io/badge/README-%ED%95%9C%EA%B5%AD%EC%96%B4-2f81f7?style=flat-square"></a>
</p>

ReachKit は、AI agent のためのクリーンな internet intake layer です。Web ページと feed を読み、GitHub を調べ、transcript と metadata を取得し、対応 platform を検索して、agent がそのまま使える小さな JSON record を返します。

agent は reasoning は得意でも、retrieval で壊れがちです。生の Web ページはノイズが多く、platform API には token が必要なことがあり、video transcript は公開 timed text がある場合だけ使えます。小さな script も、JSON に log を混ぜると tool chain では扱いづらくなります。ReachKit はその境界を、予測しやすい CLI command、stdio tool、provider diagnostic、明示的 setup guide に整理します。

公共コンテンツまたは明示的に許可されたコンテンツを扱う workflow 向けです。hidden browser extraction、login automation、crawler farm、proxy machinery、silent credential collection は行いません。URL、feed、repository、file path、platform query、post id、stock symbol、podcast feed、authorized API target を渡すと、ReachKit は安定した field を持つ normalized text record を返します。

## Agent がこれを必要とする理由

AI agent は model の弱さだけで失敗するわけではありません。input layer が不安定だと失敗します。

- 検索結果は page の存在を示しますが、reasoning には本文が必要です。
- feed、GitHub response、transcript、social post はそれぞれ違う形で届きます。
- token や dependency の不足を実行中に見つけると、その run は無駄になります。
- 単純な公共コンテンツには browser automation が重く、HTTP、parse、clean output で足ります。
- shell snippet は warning、log、data が stdout に混ざると chain しにくくなります。
- credential handling は慎重であるべきで、tool が browser profile を黙って読んだり token value を保存したりすべきではありません。

ReachKit は reasoning の前に input step を処理します。fetch、normalize、warn を行い、何が ready かを agent に伝えます。

## どこで使うか

hosted crawler や場当たり的な script ではなく、local で inspectable な retrieval layer が欲しいときに使います。

- URL、feed、repository、video、post、stock symbol、platform query が分かっている。
- agent loop、RAG ingestion、CI check、monitoring job のために stable JSON が必要。
- Web page、feed、GitHub、transcript、post、platform search を同じ result shape で扱いたい。
- `doctor` に、何が動き、何に config が必要で、次に何をすべきかを出してほしい。
- hidden session reading ではなく、明示的 env var と user-supplied file を使いたい。
- まず simple path を使い、必要な場合だけ rendered-page read を選びたい。

ReachKit は Web 全体を ranking するものではありません。既知の public source または明示的に許可された source を、agent が信頼できる record に変換します。

## 5 分でできること

```bash
reachkit setup plan
reachkit channels doctor
reachkit read url https://example.com --format json
reachkit read github owner/repo --path README.md --format json
reachkit serve stdio
```

これで agent は readiness map、Web reader、GitHub reader、stdio tool server を使えます。source ごとに別 schema を覚える必要はありません。

## 機能

| User pain | ReachKit path |
| --- | --- |
| "agent には URL があるが、使える本文が必要。" | `reachkit read url`、RSS、podcast feed、optional rendered-page reader。 |
| "agent に code と project context が必要。" | GitHub repo、file、repository search、issue、pull request、release reader。 |
| "platform content を同じ shape で扱いたい。" | YouTube、X、Xiaohongshu、Bilibili、Reddit、V2EX、LinkedIn、Xueqiu、Facebook、Instagram reader/searcher。 |
| "setup 不足で run が落ちる。" | `setup plan`、`channels doctor`、`auth status`、fix message。 |
| "agent runtime には prose ではなく tool が必要。" | `reachkit serve stdio` with `tools/list` and `tools/call`。 |
| "credential は明示的に扱いたい。" | config は env var 名と user-supplied file path だけを保存し、token value は保存しません。 |

ReachKit が現在できること：

- setup plan/install/update/remove。dry-run と safe mode に対応します。
- channels list/doctor による platform capability、provider readiness、missing config、fix guidance の確認。
- auth status/set。local config には env var 名と明示的な file path を保存し、token value はデフォルトで保存しません。
- `text/html`、`text/plain`、その他の読み取り可能な `text/*` レスポンスを持つ公共 URL の読み取り。
- URL 読み取りでは、ユーザーが明示的に指定した JSON cookie list、Netscape cookie file、Playwright storage state file を使えます。
- Python 標準ライブラリによる HTML title 抽出と本文テキスト整形。
- RSS と Atom feed の解析、および正規化済みエントリメタデータの出力。
- GitHub repository metadata、file reading、repository search、issues、pull requests、releases。
- 公開 timed text がある YouTube transcript と、明示的 API key を使う YouTube metadata/search。
- official API による X post、search、conversation query、timeline-style query。`X_BEARER_TOKEN` または `TWITTER_BEARER_TOKEN` が必要です。
- Xiaohongshu open API JSON、note search、note detail、comments。`XHS_APP_KEY` と `XHS_APP_SECRET` が必要です。
- Bilibili public video metadata と public video search。
- Reddit public search、posts、comments。
- V2EX hot topics、node topics、replies 付き topic detail、user records。
- podcast RSS metadata と episode records。
- LinkedIn public page text。
- Xueqiu quote、stock search、hot records。
- 明示的 token を使う Facebook / Instagram Graph API records。
- optional `reachkit[browser]` による、ユーザーが access できる rendered page text の読み取り。
- agent tool integration 向けの newline-delimited JSON stdio server。
- コンテンツコマンドの text / JSON 出力。

ReachKit は完全な Web クローラーではありません。browser profile の読み取り、access challenge の処理、proxy pool、fingerprint spoofing、login state の自動収集は行いません。認証が必要な path では、ユーザーが env var、cookie file、storage-state file、official API token を明示的に渡す必要があります。

## 向いている用途

ReachKit は次の用途に向いています。

- thin snippet ではなく公共 Web ページ本文が必要な AI agent tool。
- source を集めてから要約、比較、claim check を行う research assistant。
- chunking と embedding の前に stable record が必要な RAG ingestion script。
- README、docs、release、issue、repository を調べる developer agent。
- feed、changelog、public docs、platform record を監視する job。
- stdout を parseable に保つ必要がある local CLI pipeline。
- handwritten shell snippet より request/response tool を好む agent runtime。
- platform-specific content を扱いつつ、platform ごとの schema を増やしたくない workflow。

ユーザーが access できる JavaScript rendered page を読む場合は optional browser extra を使えます。大規模 crawling、access challenge handling、proxy pool、anti-abuse platform handling が必要なら、ReachKit はその層ではありません。

## インストール

ReachKit には Python 3.11 以上が必要です。

ローカル開発：

```bash
python -m pip install -e .
```

`uv` を使うと runtime を分離できます。

```bash
uv venv .venv --python 3.11
uv pip install --python .venv/Scripts/python.exe -e . pytest
```

macOS または Linux では、仮想環境の Python は通常 `.venv/bin/python` です。

Rendered page reads には optional browser extra と browser runtime が必要です。

```bash
python -m pip install -e ".[browser]"
python -m playwright install chromium
```

## Quick start

local setup plan を確認する：

```bash
reachkit setup plan
reachkit setup install --dry-run
reachkit setup install --safe
```

platform と auth status を確認する：

```bash
reachkit channels list
reachkit channels doctor
reachkit auth status
```

公共 Web ページを読む：

```bash
reachkit read url https://example.com --format json
```

feed を読む：

```bash
reachkit read rss https://example.com/feed.xml --limit 5 --format json
```

GitHub リポジトリメタデータを読む：

```bash
reachkit read github owner/repo --format json
```

GitHub リポジトリ内の公共テキストファイルを読む：

```bash
reachkit read github owner/repo --path README.md --ref main --format json
```

公開 GitHub リポジトリを検索する：

```bash
reachkit search github "agent tools" --limit 5 --format json
```

configured web endpoint を検索する：

```bash
reachkit search web "agent tools" --limit 5 --format json
```

GitHub issue、pull request、release を読む：

```bash
reachkit read github owner/repo --issue 7 --format json
reachkit read github owner/repo --pull-request 3 --format json
reachkit read github owner/repo --release v1.0.0 --format json
```

public timed text がある YouTube transcript を読む：

```bash
reachkit read youtube dQw4w9WgXcQ --lang en --format json
reachkit read youtube dQw4w9WgXcQ --metadata --format json
```

YouTube を検索する：

```bash
reachkit search youtube "agent tools" --limit 5 --format json
```

official API で X post を読む：

```bash
reachkit read x 1234567890 --format json
```

official API で X を検索する：

```bash
reachkit search x "agent tools" --limit 5 --format json
```

configured app credentials で Xiaohongshu open API JSON を読む：

```bash
reachkit read xiaohongshu /api/open/path --param note_id=abc --format json
```

BV id または av id で Bilibili public video metadata を読む：

```bash
reachkit read bilibili BV1xx411c7mD --format json
reachkit read bilibili av123456 --format json
```

その他の source を読む：

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

明示的な cookie file 付きで URL を読む：

```bash
reachkit read url https://example.com --cookie-file cookies.json --format json
```

明示的な Playwright storage state file 付きで URL を読む：

```bash
reachkit read url https://example.com --storage-state storage-state.json --format json
```

optional browser extra で rendered page text を読む：

```bash
reachkit read browser https://example.com --storage-state storage-state.json --format json
```

ローカル状態を確認する：

```bash
reachkit doctor
```

stdio tool server を起動する：

```bash
reachkit serve stdio
```

## 出力契約

コンテンツコマンドはデフォルトでプレーンテキストを出力します。`--format json` を付けると、安定した object を返します。

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

すべての content result には次が含まれます。

- `source`: `web`、`rss`、`github`、`youtube`、`x`、`xiaohongshu`、`bilibili`、`reddit`、`v2ex`、`podcast`、`linkedin`、`xueqiu`、`facebook`、`instagram`。
- `url`: request URL、または利用可能な canonical result URL。
- `title`: page、feed、repository、search、file の title。
- `content_type`: 利用可能な HTTP content type。
- `items`: 正規化済みテキストレコード。
- `warnings`: `empty_feed` や `non_html_text` などの non-fatal issue。

この形は意図的に小さくしています。agent は source ごとに新しい schema を学ぶ必要がありません。

## Stdio integration

`reachkit serve stdio` は stdin から 1 行 1 JSON object を読み、stdout に 1 行 1 JSON object を書きます。

ツール一覧：

```json
{"id":"1","method":"tools/list","params":{}}
```

ツール呼び出し：

```json
{"id":"2","method":"tools/call","params":{"name":"web_read","arguments":{"url":"https://example.com","max_chars":2000}}}
```

利用可能な tools：

- `web_read`: `url`、任意の `max_chars`、任意の `cookie_file`、任意の `storage_state`。
- `web_search`: `query`、任意の `limit`。
- `rss_read`: `url`、任意の `limit`。
- `github_read`: `repo`、任意の `path`、任意の `ref`。
- `github_search`: `query`、任意の `limit`。
- `youtube_transcript`: `video`、任意の `lang`、任意の `max_chars`。
- `youtube_metadata`: `video`。
- `youtube_search`: `query`、任意の `limit`。
- `x_read`: `post`。
- `x_search`: `query`、任意の `limit`。
- `xiaohongshu_api`: `path`、任意の `query` object。
- `xiaohongshu_read`: `path`、任意の `query` object。
- `bilibili_read`: `video`。
- `bilibili_search`: `query`、任意の `limit`。
- `reddit_read`: `target`、任意の `limit`。
- `reddit_search`: `query`、任意の `limit`。
- `v2ex_read`: `target`、任意の `limit`。
- `podcast_read`: `url`、任意の `limit`。
- `xueqiu_quote`: `symbol`。
- `xueqiu_hot`: 任意の `limit`。
- `browser_read`: `url`、任意の `storage_state`、任意の `wait_until`、任意の `max_chars`。
- `channels_list`: 引数なし。
- `channels_doctor`: 任意の `channel`。
- `auth_status`: 引数なし。
- `setup_plan`: 引数なし。

小さな request set は `examples/stdio-request.jsonl` にあります。

## Platform access

ReachKit は公開 GitHub REST endpoint を使います。token なしでも実行できますが、GitHub は unauthenticated request により厳しい rate limit を適用します。上限を上げるには `GITHUB_TOKEN` を設定します。

X post reading は official API を使い、`X_BEARER_TOKEN` または `TWITTER_BEARER_TOKEN` が必要です。

Xiaohongshu reading は open API path を使い、`XHS_APP_KEY` と `XHS_APP_SECRET` が必要です。

PowerShell では、command 実行前に credentials を設定します。

```powershell
$env:X_BEARER_TOKEN = "your_token_here"
$env:XHS_APP_KEY = "your_key"
$env:XHS_APP_SECRET = "your_secret"
```

macOS または Linux shell では：

```bash
export X_BEARER_TOKEN=your_token_here
export XHS_APP_KEY=your_key
export XHS_APP_SECRET=your_secret
```

YouTube transcript reading は、video が公開 timed text track を提供している場合に使えます。YouTube search には `YOUTUBE_API_KEY` が必要です。

Web search には `REACHKIT_WEB_SEARCH_URL` が必要です。この値は `q` と `limit` query parameter を受け取る JSON endpoint を指します。YouTube metadata は YouTube search と同じ `YOUTUBE_API_KEY` setting を使います。

Bilibili video reading/search は public metadata path が reachable な場合に利用できます。

Facebook と Instagram は Graph API を使い、明示的 token が必要です。

```powershell
$env:FACEBOOK_ACCESS_TOKEN = "your_token_here"
$env:INSTAGRAM_ACCESS_TOKEN = "your_token_here"
```

ReachKit config は env var 名と明示的 file path だけを保存します。

```bash
reachkit auth set github --token-env GITHUB_TOKEN
reachkit auth set browser --storage-state storage-state.json
reachkit auth set web --cookie-file cookies.json
```

URL reads では `--cookie-file` または `--storage-state` を使って cookie input を明示的に指定できます。ReachKit はユーザーが渡した JSON cookie list、Netscape cookie file、Playwright storage state file を読みます。これらの file は Git に入れないでください。

Rendered page reads は optional browser extra を使います。ユーザーが access できる page に対して、明示的に渡された storage state file を使えますが、ReachKit は browser profile data を抽出しません。

## 制限と動作

- `--format` は `text` と `json` を受け付けます。
- `--max-chars` のデフォルトは `12000`、範囲は `1` から `100000` です。
- `--limit` のデフォルトは `10`、上限は `50` です。
- HTTP は `http://` と `https://` のみです。
- cookie file と storage state file は明示的に指定する必要があります。ReachKit は browser profile storage を読みません。
- デフォルト HTTP timeout は `15` 秒です。
- 大きすぎるレスポンス、non-2xx response、invalid XML、invalid input、GitHub binary file は user-facing error を返します。
- 必須チェックが失敗した場合のみ、`doctor` は exit code `1` を返します。

## なぜブラウザーを使わないのか

ページに JavaScript、authentication、interaction が必要な場合、ブラウザーは便利です。ただし、ブラウザーは遅く、sandbox 化しにくく、deterministic output も作りにくくなります。

ReachKit はまず public-content path を扱います。fetch、parse、normalize を行い、小さな record を返します。そのためテストしやすく、agent loop に差し込みやすくなります。

## よくある質問

### ReachKit とは？

ReachKit は AI agent 向けの local retrieval toolkit です。公共 URL、RSS または Atom feed、GitHub resource を読み、きれいな text record を plain text または JSON で返します。

### ReachKit は AI agent のどんな問題を解くのか？

agent は新しい公共コンテキストを必要としますが、生の Web ページ、feed XML、GitHub API payload はそのまま扱いにくいです。ReachKit は「取得する、テキストを整える、有用な metadata を残す、warnings を分けて返す」という小さな契約を提供します。

### ReachKit は Web crawler ですか？

いいえ。ReachKit は focused public content reader です。single URL、feed、GitHub repository metadata、GitHub text file、GitHub repository search を扱います。サイト全体の crawling、JavaScript rendering、login-only content は扱いません。

### Hosted web search API との違いは？

ranking、scale、managed crawling、JavaScript rendering、cited research が必要な場合、hosted search and extraction API は便利です。ReachKit はより軽い local path のためのものです。predictable CLI commands、stdio integration、必須ではない paid API、テストしやすい outputs を重視します。

### ReachKit は RAG pipeline に入力できますか？

はい。公共ページ、feed、GitHub resources に使えます。ReachKit はこれらを normalized text records に変換し、RAG ingestion script が chunk、embed、store、score できるようにします。

### どんな検索で見つけられるべきですか？

ReachKit は "Python CLI for AI agent web retrieval"、"AI agent tool for reading public URLs"、"RSS to JSON command line tool"、"GitHub repository search CLI JSON"、"stdio tools/list tools/call Python server"、"public web page to clean text Python"、"GitHub README reader for AI agents" のような検索に向いています。

## Development

テスト実行：

```bash
python -m pytest -q
```

smoke check：

```bash
reachkit doctor
reachkit read url https://example.com --format json
```

テストスイートは可能な範囲で fixture と mocked HTTP path を使うため、通常のテストは live website に依存しません。

## License

Apache-2.0. See `LICENSE`.
