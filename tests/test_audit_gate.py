from __future__ import annotations

import shutil
import subprocess


def test_public_surface_audit_script_passes_on_repository():
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/audit-public-surface.ps1"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "audit passed" in result.stdout.lower()


def test_public_surface_audit_script_supports_windows_powershell_when_available():
    if not shutil.which("powershell"):
        return

    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/audit-public-surface.ps1"],
        check=False,
        capture_output=True,
    )
    output = (result.stdout or b"").decode("utf-8", errors="replace")
    output += (result.stderr or b"").decode("utf-8", errors="replace")

    assert result.returncode == 0, output
    assert "audit passed" in output.lower()


def test_public_surface_audit_script_fails_on_forbidden_public_text(tmp_path):
    if not shutil.which("pwsh"):
        return
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".gitignore").write_text("docs/Implementation-Plan.md\n", encoding="utf-8")
    forbidden_text = "source " + "provenance marker\n"
    (repo / "README.md").write_text(forbidden_text, encoding="utf-8")
    scripts = repo / "scripts"
    scripts.mkdir()
    script_copy = scripts / "audit-public-surface.ps1"
    script_copy.write_text((__import__("pathlib").Path("scripts/audit-public-surface.ps1")).read_text(encoding="utf-8"), encoding="utf-8")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)

    result = subprocess.run(
        ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_copy)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "forbidden wording" in (result.stdout + result.stderr).lower()
