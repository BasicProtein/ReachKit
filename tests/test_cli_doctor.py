import json

from reachkit.cli import app
from reachkit.core.models import DiagnosticIssue


def test_doctor_outputs_json_and_returns_zero(monkeypatch, capsys):
    from reachkit.cli.commands import doctor

    monkeypatch.setattr(
        doctor,
        "run_doctor",
        lambda: [
            DiagnosticIssue(
                code="python_version",
                level="ok",
                message="Python version is valid.",
                required=True,
            )
        ],
    )

    exit_code = app.main(["doctor", "--format", "json"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["issues"][0]["code"] == "python_version"


def test_doctor_returns_one_for_required_error(monkeypatch, capsys):
    from reachkit.cli.commands import doctor

    monkeypatch.setattr(
        doctor,
        "run_doctor",
        lambda: [
            DiagnosticIssue(
                code="python_version",
                level="error",
                message="Python 3.11 or newer is required.",
                required=True,
            )
        ],
    )

    exit_code = app.main(["doctor"])

    assert exit_code == 1
    assert "python_version" in capsys.readouterr().out
