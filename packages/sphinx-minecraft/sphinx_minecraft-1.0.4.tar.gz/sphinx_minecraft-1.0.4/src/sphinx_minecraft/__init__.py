from enum import Enum
from importlib import metadata
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx_treeview.decorator import DecoratorType, images_to_decorator_icons


BASE_DIR = Path(__file__).parent

logger = logging.getLogger(__name__)


class DectoratorRegistry(Enum):
    MCDIR = "mcdir"
    NBT = "nbt"


def setup(app: Sphinx):
    app.setup_extension('sphinx_treeview')

    for decorator in DectoratorRegistry:
        app.config.stv_decorators.append(DecoratorType(
            decorator.value,
            images_to_decorator_icons(BASE_DIR / "icons" / decorator.value),
        ))
        logger.verbose(f"Tree decorator '{decorator.value}' added.")

    return {
        "version": metadata.version("sphinx-minecraft"),
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
