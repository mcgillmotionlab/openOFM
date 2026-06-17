"""Basic import tests to verify the package installs and loads correctly."""


def test_import_openofm():
    import openofm  # noqa: F401


def test_import_submodules():
    from openofm import static, dynamic, validate  # noqa: F401
