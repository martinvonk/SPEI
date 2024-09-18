from importlib import metadata
from platform import python_version

__version__ = "0.5.0"


def show_versions() -> str:
    msg = f"Versions\npython: {python_version()}\nspei: {__version__}\n"

    requirements = metadata.requires("spei")
    if requirements:
        deps = [x for x in requirements if "extra" not in x]
        for dep in deps:
            msg += f"{dep}: {metadata.version(dep)}\n"

    return msg
