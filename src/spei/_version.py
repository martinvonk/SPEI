from importlib import metadata
from platform import python_version

from packaging.requirements import Requirement

__version__ = "0.8.2"


def get_versions() -> dict[str, str]:
    versionsd = {"python": f"{python_version()}", "spei": f"{__version__}"}

    requirements = metadata.requires("spei")
    if requirements:
        deps = [Requirement(x).name for x in requirements if "extra" not in x]
        for dep in deps:
            versionsd[dep] = metadata.version(dep)
    return versionsd


def show_versions() -> str:
    versionsd = get_versions()
    msg = "\n".join(f"{key}: {value}" for key, value in versionsd.items())
    return msg
