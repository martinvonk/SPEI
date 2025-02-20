from importlib import metadata
from platform import python_version

__version__ = "0.6.1"


def show_versions() -> str:
    msg = f"python: {python_version()}\nspei: {__version__}\n"

    requirements = metadata.requires("spei")
    if requirements:
        deps = [x for x in requirements if "extra" not in x]
        for dep in deps:
            msg += f"{dep}: {metadata.version(dep)}"
            msg += "\n" if deps.index(dep) < len(deps) - 1 else ""

    return msg
