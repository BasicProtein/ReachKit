from __future__ import annotations


class ReachKitError(Exception):
    exit_code = 1


class InputError(ReachKitError):
    pass


class FetchError(ReachKitError):
    pass


class ParseError(ReachKitError):
    pass


class ConfigError(ReachKitError):
    pass


def exit_code_for_error(error: BaseException) -> int:
    if isinstance(error, ReachKitError):
        return error.exit_code
    return 3
