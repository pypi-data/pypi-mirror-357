from importlib import resources
from importlib.abc import Traversable
from typing import Tuple

from .data import METADATA_FILENAME, POLYGONS_FILENAME


def get_data() -> Tuple[str, Traversable, Traversable]:
    return (
        "CAN",
        resources.files("coord2loc_can.data").joinpath(POLYGONS_FILENAME),
        resources.files("coord2loc_can.data").joinpath(METADATA_FILENAME),
    )
