"""
Configuration of wily.

TODO : Handle operator settings. Maybe a section for each operator and then pass kwargs to operators?
TODO : Better utilise default values and factory in @dataclass to replace DEFAULT_CONFIG
 and replace the logic in load() to set default values.
"""
from functools import lru_cache
import configparser
import logging
import pathlib
import hashlib
from dataclasses import dataclass, field
from typing import Any, List, Union, Set, Optional

logger = logging.getLogger(__name__)


@lru_cache(maxsize=128)
def generate_cache_path(path: pathlib.Path) -> pathlib.Path:
    """
    Generate a reusable path to cache results.

    Will use the --path of the target and hash into
    a 9-character directory within the HOME folder.

    :return: The cache path
    """
    logger.debug(f"Generating cache for {path}")
    sha = hashlib.sha1(str(path).encode()).hexdigest()[:9]
    HOME = pathlib.Path.home()
    cache_path = HOME / ".wily" / sha
    logger.debug(f"Cache path is {cache_path}")
    return cache_path


@dataclass
class WilyConfig(object):
    """
    Wily configuration.

    A data class to reflect the configurable options within Wily.
    """

    operators: Set[str]
    archiver: Any
    path: str
    max_revisions: int
    targets: Optional[List[str]] = None
    include_ipynb: bool = True
    ipynb_cells: bool = True
    checkout_options: dict = field(default_factory=dict)

    def __post_init__(self):
        """Clone targets as a list of path."""
        if self.targets is None or "":
            self.targets = [self.path]
        self._cache_path = None

    @property
    def cache_path(self) -> pathlib.Path:
        """Path to the cache."""
        if not self._cache_path:
            self._cache_path = generate_cache_path(pathlib.Path(self.path).absolute())
        return self._cache_path

    @cache_path.setter
    def cache_path(self, value: pathlib.Path):
        """Override the cache path."""
        logger.debug(f"Setting custom cache path to {value}")
        self._cache_path = value


# Default values for Wily

""" The default operators """
DEFAULT_OPERATORS = {"raw", "maintainability", "cyclomatic", "halstead"}

""" The name of the default archiver """
DEFAULT_ARCHIVER = "git"

""" The default configuration file name """
DEFAULT_CONFIG_PATH = "wily.cfg"

""" The default section name in the config """
DEFAULT_CONFIG_SECTION = "wily"

""" The default maximum number of revisions to archiver """
DEFAULT_MAX_REVISIONS = 50

DEFAULT_PATH = "."

""" The default configuration for Wily (if no config file exists) """
DEFAULT_CONFIG = WilyConfig(
    operators=DEFAULT_OPERATORS,
    archiver=DEFAULT_ARCHIVER,
    path=DEFAULT_PATH,
    max_revisions=DEFAULT_MAX_REVISIONS,
)

""" Default table style in console. See tabulate docs for more. """
DEFAULT_GRID_STYLE = "fancy_grid"


def load(config_path: Union[str, pathlib.Path] = DEFAULT_CONFIG_PATH) -> WilyConfig:
    """
    Load config file and set values to defaults where no present.

    :return: The configuration ``WilyConfig``
    :rtype: :class:`wily.config.WilyConfig`
    """
    if not pathlib.Path(config_path).exists():
        logger.debug(f"Could not locate {config_path}, using default config.")
        return DEFAULT_CONFIG

    config = configparser.ConfigParser(default_section=DEFAULT_CONFIG_SECTION)
    config.read(config_path)

    operators = config.get(
        section=DEFAULT_CONFIG_SECTION, option="operators", fallback=DEFAULT_OPERATORS
    )
    archiver = config.get(
        section=DEFAULT_CONFIG_SECTION, option="archiver", fallback=DEFAULT_ARCHIVER
    )
    path = config.get(section=DEFAULT_CONFIG_SECTION, option="path", fallback=".")
    max_revisions = config.getint(
        section=DEFAULT_CONFIG_SECTION,
        option="max_revisions",
        fallback=DEFAULT_MAX_REVISIONS,
    )
    include_ipynb = config.getboolean(
        section=DEFAULT_CONFIG_SECTION, option="include_ipynb", fallback=True
    )
    ipynb_cells = config.getboolean(
        section=DEFAULT_CONFIG_SECTION, option="ipynb_cells", fallback=True
    )

    return WilyConfig(
        operators=operators,
        archiver=archiver,
        path=path,
        max_revisions=max_revisions,
        include_ipynb=include_ipynb,
        ipynb_cells=ipynb_cells,
    )