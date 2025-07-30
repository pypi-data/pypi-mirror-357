# CZTile provides a set of tiling strategies
# Copyright 2022 Carl Zeiss Microscopy GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# To obtain a commercial version please contact Carl Zeiss Microscopy GmbH.
"""Contains all tiling strategies supported by cztile"""
from dataclasses import dataclass
from typing import List, NamedTuple, Union, Tuple
from abc import abstractmethod, ABCMeta

Rectangle = NamedTuple("Rectangle", [("x", int), ("y", int), ("w", int), ("h", int)])


@dataclass
class Tile1d:
    """A single 1D tile.

    Attributes:
        left_most_tile_pixel: the left-most pixel belonging to the tile
        width: the width of the tile interior (excluding borders)
        left_border_width: the width of the left border
        right_border_width: the width of the right border
    """

    left_most_tile_pixel: int
    width: int
    left_border_width: int
    right_border_width: int


@dataclass
class TileBorder2D:
    """A 2D border.

    Attributes:
        left: the left border size
        top: the top border size
        right: the right border size
        bottom: the bottom border size
    """

    left: int
    top: int
    right: int
    bottom: int


class Tile2D:
    """A 2D tile.

    Attributes:
        roi: the tile roi
        border: the tile border
    """

    center: Rectangle
    border: TileBorder2D
    roi: Rectangle

    def __init__(self, center: Union[Tuple[int, int, int, int], Rectangle], border: TileBorder2D) -> None:
        """Initializes a 2D tile.

        Args:
            center: the tile center
            border: the tile border
        """
        self.center = Rectangle(*center)
        self.border = border
        self.roi = Rectangle(
            x=self.center.x - self.border.left,
            y=self.center.y - self.border.top,
            w=self.center.w + self.border.left + self.border.right,
            h=self.center.h + self.border.top + self.border.bottom,
        )

    def __eq__(self, other: object) -> bool:
        """Implementation of the equal operator for a 2D tile."""
        # Taken from https://stackoverflow.com/questions/54801832/mypy-eq-incompatible-with-supertype-object
        # Also refer to https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
        if not isinstance(other, Tile2D):
            # If we return NotImplemented, Python will automatically try
            # running other.__eq__(self), in case 'other' knows what to do with Tile2D objects.
            return NotImplemented
        return self.center == other.center and self.border == other.border and self.roi == other.roi


class TilingStrategy2D(metaclass=ABCMeta):
    """Base module for creating a strategy to store the data samples on disk in a defined format"""

    @abstractmethod
    def tile_rectangle(self, rectangle: Union[Tuple[int, int, int, int], Rectangle]) -> List[Tile2D]:
        """Tiles the provided rectangle.

        Args:
            rectangle: The rectangle to tile.

        Returns:
            A list with the tiles covering the specified rectangle.
        """
