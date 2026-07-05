import importlib

import pytest


def test_help_returns_zero_and_prints_product_name(capsys):
    try:
        app = importlib.import_module("reachkit.cli.app")
    except ModuleNotFoundError as exc:
        pytest.fail(f"CLI module is not importable: {exc}")

    exit_code = app.main(["--help"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "ReachKit" in captured.out


def test_version_prints_package_version(capsys):
    try:
        app = importlib.import_module("reachkit.cli.app")
    except ModuleNotFoundError as exc:
        pytest.fail(f"CLI module is not importable: {exc}")

    exit_code = app.main(["--version"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "0.1.0\n"
