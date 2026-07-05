# ReachKit

<p align="center">
  <a href="README.zh-CN.md"><img alt="中文" src="https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87-2f81f7?style=flat-square"></a>
  <a href="../README.md"><img alt="English" src="https://img.shields.io/badge/README-English-2f81f7?style=flat-square"></a>
  <a href="README.ja.md"><img alt="日本語" src="https://img.shields.io/badge/README-%E6%97%A5%E6%9C%AC%E8%AA%9E-2f81f7?style=flat-square"></a>
  <a href="README.ko.md"><img alt="한국어" src="https://img.shields.io/badge/README-%ED%95%9C%EA%B5%AD%EC%96%B4-2f81f7?style=flat-square"></a>
</p>

ReachKit は、AI agent が公共の Web ページ、RSS または Atom feed、GitHub コンテンツ、YouTube transcript、X post、Xiaohongshu open API JSON、Bilibili video metadata を安定して読むための Python CLI とライブラリです。

ブラウザーセッション、ログインフロー、クローラー基盤、有料検索スタックを使わずに取得処理を行いたい agent ワークフロー向けです。公共 URL、feed、リポジトリ、ファイルパス、GitHub 検索クエリ、YouTube video、X post id、Xiaohongshu open API path、Bilibili video idを渡すと、ReachKit は安定した JSON フィールドを持つ正規化済みテキストレコードを返します。agent はそれを確認、引用、保存、順位付け、次のツールへの入力に使えます。

## ReachKit が必要な理由

AI agent は公共コンテキストを取得するとき、同じ問題に何度もぶつかります。

- 検索スニペットだけでは推論に足りません。agent にはタイトルと URL だけでなく、ページ本文、feed エントリ、リポジトリメタデータ、ファイル内容が必要です。
- Web コンテンツの形式はばらばらです。HTML、プレーンテキスト、RSS、Atom、GitHub API payload は、それぞれ解析してからでないと使いにくいです。
- 単純な公共コンテンツにはブラウザー自動化が重すぎます。多くの処理は HTTP、テキスト整形、予測しやすい出力だけで足ります。
- その場限りのスクリプトは信頼しにくいです。あるコマンドは文章を出し、別のコマンドは不完全な JSON を出し、別のコマンドは stdout に警告を混ぜます。
- agent の tool call には契約が必要です。返り値の形が毎回変わるツールは、処理の連鎖に入れづらくなります。
- 公開リポジトリも調査対象です。agent は README、概要、言語、stars、default branch、GitHub 検索結果を必要とすることがあります。
- ローカル診断は重要です。GitHub token の不足、HTTPS runtime の問題、UTF-8 ではないコンソールは、1 回の実行を丸ごと無駄にします。

ReachKit は「agent が公共コンテキストを必要としている」状態から「agent が推論に使えるきれいなテキストを得る」状態までの、地味だけれど重要な層を担当します。

## どこで使うか

Web 検索、クロール、JavaScript レンダリング、Markdown 抽出、ランキング、マネージドリサーチには、強力なホスト型 API があります。ReachKit は、もっと小さくローカルな、それでも信頼性が必要な仕事に向いています。

- 読みたい公共 URL、feed、リポジトリ、GitHub クエリがすでに分かっている。
- Python コマンドとして CI、ローカルスクリプト、agent sandbox で動かしたい。
- 次のツールが解析しやすいように、stdout を機械可読に保ちたい。
- サイレントな部分出力ではなく、明示的な警告と型のあるエラーが欲しい。
- 公共 Web ページ、feed、GitHub メタデータ、GitHub テキストファイルを同じ取得経路で扱いたい。
- RAG、要約、監視、開発者調査のための低設定な入力段階が必要。

要するに、ReachKit は Web 全体のランキングを解く道具ではありません。既知の公共ソースを、agent が信頼できるきれいなレコードに変えるための道具です。

## 機能

ReachKit が現在できること：

- `text/html`、`text/plain`、その他の読み取り可能な `text/*` レスポンスを持つ公共 URL の読み取り。
- URL 読み取りでは、ユーザーが明示的に指定した JSON cookie list、Netscape cookie file、Playwright storage state file を使えます。
- Python 標準ライブラリによる HTML title 抽出と本文テキスト整形。
- RSS と Atom feed の解析、および正規化済みエントリメタデータの出力。
- 公開 GitHub REST API によるリポジトリメタデータの読み取り。
- GitHub contents API によるリポジトリ内テキストファイルの読み取り。base64 テキストファイルにも対応します。
- 公開 GitHub リポジトリ検索と安定した項目フィールド。
- 公開 timed text がある YouTube transcript の読み取り。
- official API による X post の読み取り。`X_BEARER_TOKEN` または `TWITTER_BEARER_TOKEN` が必要です。
- Xiaohongshu open API JSON の読み取り。`XHS_APP_KEY` と `XHS_APP_SECRET` が必要です。
- BV video id に対する Bilibili public video metadata の読み取り。
- optional `reachkit[browser]` による、ユーザーが access できる rendered page text の読み取り。
- Python バージョン、UTF-8 I/O、HTTPS runtime、GitHub token、ネットワークを確認する `doctor` コマンド。
- agent tool integration 向けの newline-delimited JSON stdio server。
- コンテンツコマンドの text / JSON 出力。

ReachKit は完全な Web クローラーではありません。browser profile の読み取り、access challenge の処理、proxy pool、login-only page は扱いません。URL 読み取りで cookie を使うのは、ユーザーが cookie file を明示的に指定した場合だけです。

## 向いている用途

ReachKit は次の用途に向いています。

- 公共 Web ページ本文を必要とする AI agent tool。
- YouTube transcript text、X post text、Xiaohongshu open API JSON、Bilibili video metadata を他の source と同じ JSON shape で扱う workflow。
- README、docs ページ、release feed の取得ワークフロー。
- RSS または Atom feed を読んでから要約する research assistant。
- developer agent 向けの GitHub repository discovery tool。
- deterministic JSON が必要なローカル CLI pipeline。
- request / response object を期待する agent runtime 向け stdio tool。
- 公共ページと feed の軽量 RAG ingestion script。
- 公開 docs、changelog、feed、GitHub file を監視する CI check。
- ブラウザーを起動せずに Web、feed、repository context が必要な developer research script。

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

public timed text がある YouTube transcript を読む：

```bash
reachkit read youtube dQw4w9WgXcQ --lang en --format json
```

official API で X post を読む：

```bash
reachkit read x 1234567890 --format json
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

- `source`: `web`、`rss`、`github`、`youtube`、`x`、`xiaohongshu`、`bilibili`。
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
- `rss_read`: `url`、任意の `limit`。
- `github_read`: `repo`、任意の `path`、任意の `ref`。
- `github_search`: `query`、任意の `limit`。
- `youtube_transcript`: `video`、任意の `lang`、任意の `max_chars`。
- `x_read`: `post`。
- `xiaohongshu_api`: `path`、任意の `query` object。
- `bilibili_read`: `video`。
- `browser_read`: `url`、任意の `storage_state`、任意の `wait_until`、任意の `max_chars`。

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

YouTube transcript reading は、video が公開 timed text track を提供している場合に使えます。すべての video が public transcript を提供するわけではありません。

Bilibili video reading は BV id の public metadata を取得します。

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
