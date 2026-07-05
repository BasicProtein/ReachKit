from reachkit.diagnostics import doctor


def test_run_doctor_returns_required_and_warning_checks(monkeypatch):
    monkeypatch.setattr(doctor.sys, "version_info", (3, 11, 0))
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    issues = doctor.run_doctor(include_network=False)

    by_code = {issue.code: issue for issue in issues}
    assert by_code["python_version"].level == "ok"
    assert by_code["utf8_io"].required is True
    assert by_code["https_runtime"].required is True
    assert by_code["github_token"].level == "warning"
    assert doctor.required_checks_failed(issues) is False


def test_required_checks_failed_detects_required_error():
    issues = [
        doctor.DiagnosticIssue(
            code="python_version",
            level="error",
            message="Python 3.11 or newer is required.",
            required=True,
        )
    ]

    assert doctor.required_checks_failed(issues) is True


def test_network_failure_is_warning(monkeypatch):
    def fail(url):
        raise OSError("network down")

    monkeypatch.setattr(doctor, "fetch_text", fail)

    issue = doctor.check_network_example()

    assert issue.code == "network_example"
    assert issue.level == "warning"
