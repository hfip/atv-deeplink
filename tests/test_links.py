import json

import pytest

from atv_deeplink import build, decode_target, get_by_scheme, validate
from atv_deeplink.cli import main


def test_build_infuse_link():
    url = build("infuse", "smb://nas/media/Movie.mkv")
    assert url.startswith("infuse://x-callback-url/play?url=")
    assert decode_target(url) == "smb://nas/media/Movie.mkv"


def test_build_encodes_spaces_and_arabic():
    url = build("infuse", "smb://nas/فيلم جديد.mkv")
    assert " " not in url
    assert decode_target(url) == "smb://nas/فيلم جديد.mkv"


def test_build_vlc_link():
    assert build("vlc", "http://example.com/a.mkv").startswith(
        "vlc-x-callback://x-callback-url/stream?"
    )


def test_build_youtube_uses_video_id():
    url = build("youtube", "dQw4w9WgXcQ")
    assert url.startswith("youtube://watch?v=")
    assert decode_target(url, "v") == "dQw4w9WgXcQ"


def test_unknown_app_is_rejected():
    with pytest.raises(ValueError):
        build("quicktime", "x")


def test_scheme_lookup():
    assert get_by_scheme("vlc-x-callback").key == "vlc"
    assert get_by_scheme("nope") is None


def test_validate_accepts_a_good_link():
    result = validate(build("infuse", "smb://nas/movie.mkv"))
    assert result.ok
    assert result.problems == []


def test_validate_rejects_web_urls():
    result = validate("https://example.com/movie.mkv")
    assert not result.ok


def test_validate_flags_missing_parameter():
    result = validate("infuse://x-callback-url/play")
    assert not result.ok
    assert any("url" in problem.message for problem in result.problems)


def test_validate_flags_empty_parameter():
    result = validate("infuse://x-callback-url/play?url=")
    assert not result.ok


def test_validate_warns_on_unknown_scheme():
    result = validate("plex://play?url=x")
    assert result.ok
    assert result.problems[0].level == "warning"


def test_validate_flags_raw_spaces():
    result = validate("infuse://x-callback-url/play?url=a b")
    assert not result.ok
    assert any("space" in problem.message for problem in result.problems)


def test_validate_flags_double_encoding():
    result = validate("infuse://x-callback-url/play?url=smb%253A%252F%252Fnas")
    assert any("double" in problem.message for problem in result.problems)


def test_cli_build(capsys):
    assert main(["build", "infuse", "smb://nas/movie.mkv"]) == 0
    assert capsys.readouterr().out.strip().startswith("infuse://")


def test_cli_build_json(capsys):
    assert main(["--json", "build", "infuse", "smb://nas/movie.mkv"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["target"] == "smb://nas/movie.mkv"


def test_cli_check_ok(capsys):
    url = build("infuse", "smb://nas/movie.mkv")
    assert main(["check", url]) == 0
    assert "ok" in capsys.readouterr().out


def test_cli_check_fails_on_error():
    assert main(["check", "https://example.com"]) == 1


def test_cli_apps(capsys):
    assert main(["apps"]) == 0
    output = capsys.readouterr().out
    assert "infuse" in output and "vlc" in output and "youtube" in output


def test_cli_without_command_returns_two():
    assert main([]) == 2
