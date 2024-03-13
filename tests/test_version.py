import spei as si


def test_version() -> None:
    assert isinstance(si.__version__, str)
    assert si.__version__.count(".") == 2


def test_show_versions():
    msg = si.show_versions()
    assert isinstance(msg, str)
