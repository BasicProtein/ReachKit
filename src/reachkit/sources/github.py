from __future__ import annotations

import base64
from collections.abc import Callable
import json
import os
from urllib.parse import quote, urlencode

from reachkit.core.errors import InputError, ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.text import compact_text
from reachkit.runtime.http import HttpResponse, fetch_text
from reachkit.runtime.limits import DEFAULT_LIMIT, MAX_LIMIT

FetchText = Callable[..., HttpResponse]


def parse_repo_spec(repo: str) -> tuple[str, str]:
    parts = [part for part in repo.split("/") if part]
    if len(parts) != 2:
        raise InputError("Repository must use owner/name format")
    return parts[0], parts[1]


def _headers() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _load_json(response: HttpResponse):
    try:
        return json.loads(response.body)
    except json.JSONDecodeError as exc:
        raise ParseError("GitHub response was not valid JSON") from exc


def _is_binary(data: bytes) -> bool:
    return b"\x00" in data


class GitHubReader:
    name = "github"

    def __init__(self, fetcher: FetchText | None = None) -> None:
        self._fetcher = fetcher

    def read(self, repo: str, path: str | None = None, ref: str | None = None) -> SourceResult:
        owner, name = parse_repo_spec(repo)
        if path:
            return self.read_file(owner, name, path, ref=ref)
        return self.read_repo(owner, name)

    def read_repo(self, owner: str, repo: str) -> SourceResult:
        url = f"https://api.github.com/repos/{quote(owner)}/{quote(repo)}"
        active_fetcher = self._fetcher or fetch_text
        response = active_fetcher(url, headers=_headers())
        data = _load_json(response)
        full_name = str(data.get("full_name") or f"{owner}/{repo}")
        html_url = str(data.get("html_url") or f"https://github.com/{owner}/{repo}")
        description = data.get("description")
        default_branch = data.get("default_branch")
        stars = data.get("stargazers_count")
        language = data.get("language")
        lines = [full_name]
        if description:
            lines.append(str(description))
        if default_branch:
            lines.append(f"default branch: {default_branch}")
        if stars is not None:
            lines.append(f"stars: {stars}")
        if language:
            lines.append(f"language: {language}")
        item = RetrievedItem(
            title=full_name,
            url=html_url,
            text=compact_text("\n".join(lines)),
            metadata={"default_branch": default_branch, "stars": stars, "language": language},
        )
        return SourceResult(self.name, html_url, full_name, response.headers.get("Content-Type"), [item], [])

    def read_file(self, owner: str, repo: str, path: str, ref: str | None = None) -> SourceResult:
        encoded_path = "/".join(quote(part) for part in path.split("/"))
        url = f"https://api.github.com/repos/{quote(owner)}/{quote(repo)}/contents/{encoded_path}"
        if ref:
            url = f"{url}?{urlencode({'ref': ref})}"
        active_fetcher = self._fetcher or fetch_text
        response = active_fetcher(url, headers=_headers())
        data = _load_json(response)
        if isinstance(data, list):
            raise InputError("Directory listings are not available")
        if not isinstance(data, dict):
            raise ParseError("GitHub file response was not an object")
        if data.get("encoding") != "base64":
            raise ParseError("GitHub file encoding is not handled")
        try:
            decoded = base64.b64decode(str(data.get("content") or ""), validate=False)
        except ValueError as exc:
            raise ParseError("GitHub file content could not be decoded") from exc
        if _is_binary(decoded):
            raise ParseError("GitHub file appears to be binary")
        text = compact_text(decoded.decode("utf-8", errors="replace"))
        item = RetrievedItem(
            title=str(data.get("path") or path),
            url=data.get("html_url"),
            text=text,
            metadata={"path": data.get("path") or path},
        )
        return SourceResult(self.name, response.url, item.title, response.headers.get("Content-Type"), [item], [])

    def search(self, query: str, limit: int = DEFAULT_LIMIT) -> SourceResult:
        active_limit = min(max(1, limit), MAX_LIMIT)
        url = "https://api.github.com/search/repositories?" + urlencode({"q": query, "per_page": active_limit})
        active_fetcher = self._fetcher or fetch_text
        response = active_fetcher(url, headers=_headers())
        data = _load_json(response)
        items: list[RetrievedItem] = []
        for repo in list(data.get("items") or [])[:active_limit]:
            full_name = str(repo.get("full_name") or "")
            html_url = repo.get("html_url")
            description = repo.get("description")
            default_branch = repo.get("default_branch")
            stars = repo.get("stargazers_count")
            language = repo.get("language")
            lines = [full_name]
            if description:
                lines.append(str(description))
            if default_branch:
                lines.append(f"default branch: {default_branch}")
            if stars is not None:
                lines.append(f"stars: {stars}")
            if language:
                lines.append(f"language: {language}")
            items.append(
                RetrievedItem(
                    title=full_name,
                    url=html_url,
                    text=compact_text("\n".join(lines)),
                    metadata={"default_branch": default_branch, "stars": stars, "language": language},
                )
            )
        return SourceResult(self.name, url, f"GitHub search: {query}", response.headers.get("Content-Type"), items, [])

    def search_repositories(self, query: str, limit: int = DEFAULT_LIMIT) -> SourceResult:
        return self.search(query, limit=limit)
