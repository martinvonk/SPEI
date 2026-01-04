import spei as si


def test_version() -> None:
    assert isinstance(si.__version__, str)
    assert si.__version__.count(".") == 2


def test_get_versions():
    versionsd = si._version.get_versions()
    assert isinstance(versionsd, dict)
    assert "python" in versionsd
    assert "spei" in versionsd


def test_show_versions():
    msg = si.show_versions()
    assert isinstance(msg, str)
