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
"""Provides tiling primitives for the DNN tiling strategy.

This is a python implementation of the algorithm described in README.
"""
import sys
from math import ceil, floor
from typing import List, Union, Tuple
from cztile.tiling_strategy import TilingStrategy2D, Rectangle, Tile2D, TileBorder2D, Tile1d


class AlmostEqualBorderFixedTotalAreaStrategy2D(TilingStrategy2D):
    """A 2D tiling strategy that covers a total area with a minimal number of tiles of constant
    total area such that:
        a) all interior tiles have at least a minimum border width/height on all sides
        b) the edge tiles have zero border at the edge and at least the minimum border width
           on their inner sides.
        c) The sizes of all non-zero borders differ at most by one pixel.

    Attributes:
        total_tile_width    The fixed total widths (inc. border) of the tiles to generate.
        total_tile_height   The fixed total heights (inc. border) of the tiles to generate.
        min_border_width    The minimum width of each of the interior borders.
    """

    def __init__(self, total_tile_width: int, total_tile_height: int, min_border_width: int) -> None:
        """Initializes an AlmostEqualBorderFixedTotalAreaStrategy2D.

        Args:
            total_tile_width: The fixed total widths (inc. border) of the tiles to generate.
            total_tile_height: The fixed total heights (inc. border) of the tiles to generate.
            min_border_width: The minimum width of each of the interior borders.
        """
        self.total_tile_width = total_tile_width
        self.total_tile_height = total_tile_height
        self.min_border_width = min_border_width

        self.horizontal_tiler = Tiler1d(total_tile_width=total_tile_width, min_border_width=min_border_width)
        self.vertical_tiler = Tiler1d(total_tile_width=total_tile_height, min_border_width=min_border_width)

    def tile_rectangle(self, rectangle: Union[Tuple[int, int, int, int], Rectangle]) -> List[Tile2D]:
        """Tiles the provided rectangle.

        Args:
            rectangle: The rectangle to tile.

        Returns:
            A list with the tiles covering the specified rectangle.
        """
        rectangle = Rectangle(*rectangle)
        if rectangle.w * rectangle.h == 0:
            return []

        horizontal_tiles = self.horizontal_tiler.calculate_tiles(rectangle.w)
        vertical_tiles = self.vertical_tiler.calculate_tiles(rectangle.h)

        result: List[Tile2D] = []
        for horizontal_tile in horizontal_tiles:
            for vertical_tile in vertical_tiles:
                tile_center = Rectangle(
                    x=rectangle.x + horizontal_tile.left_most_tile_pixel,
                    y=rectangle.y + vertical_tile.left_most_tile_pixel,
                    w=horizontal_tile.width,
                    h=vertical_tile.width,
                )
                tile_border = TileBorder2D(
                    left=horizontal_tile.left_border_width,
                    top=vertical_tile.left_border_width,
                    right=horizontal_tile.right_border_width,
                    bottom=vertical_tile.right_border_width,
                )
                result.append(Tile2D(center=tile_center, border=tile_border))

        return result


class Tiler1d:
    """Tiles an integer interval beginning at 0 with tiles having a fixed total width and with zero outer borders.

    Attributes:
        total_tile_width    The fixed total widths of the tiles to generate.
        min_border_width    The minimum width of each of the interior borders.
    """

    def __init__(self, total_tile_width: int, min_border_width: int) -> None:
        """Initializes a 1D tiler.

        Args:
            total_tile_width: The fixed total widths of the tiles to generate.
            min_border_width: The minimum width of each of the interior borders.

        Raises:
            ValueError: For invalid total tile or min border width
        """
        if total_tile_width <= 0:
            raise ValueError("Total tile width must be greater than zero.")
        if min_border_width < 0:
            raise ValueError("Minimum border width cannot be negative.")
        if min_border_width > sys.maxsize / 2:
            raise ValueError(f"Minimum border width is too large. It needs to be smaller than {sys.maxsize / 2}.")

        self.total_tile_width = total_tile_width
        self.min_border_width = min_border_width
        if 2 * min_border_width >= total_tile_width:
            raise ValueError("Minimum border width must be less than half the tile size.")

    def calculate_tiles(self, image_width: int) -> List[Tile1d]:
        """Calculates a tiling of the specified image width.

        Args:
            image_width: The width of the image.

        Returns:
            A list of tiles covering the specified image_width.

        Raises:
            AssertionError: Border misconfigurations
        """
        if image_width < self.total_tile_width:
            border_width = self.total_tile_width - image_width
            left_border = border_width // 2
            right_border = border_width - left_border
            return [Tile1d(0, image_width, left_border, right_border)]

        if image_width == self.total_tile_width:
            return [Tile1d(0, self.total_tile_width, 0, 0)]

        max_width_of_edge_tiles: int = self.total_tile_width - self.min_border_width
        max_width_of_interior_tiles: int = self.total_tile_width - 2 * self.min_border_width
        interior: int = max(0, image_width - 2 * max_width_of_edge_tiles)

        number_of_tiles: int = ceil(interior * 1.0 / max_width_of_interior_tiles) + 2
        number_of_non_zero_borders: int = 2 * number_of_tiles - 2

        excess_border: float = (
            2.0 * max_width_of_edge_tiles + (number_of_tiles - 2) * max_width_of_interior_tiles - image_width
        )

        fractional_excess_border: float = excess_border / number_of_non_zero_borders
        fractional_border_width: float = fractional_excess_border + self.min_border_width

        cumulative_border: List[int] = [0] * (number_of_non_zero_borders + 1)
        for j in range(0, number_of_non_zero_borders + 1):
            cbj: float = j * fractional_border_width
            cumulative_border[j] = floor(cbj)

        tile_boundaries: List[int] = [0] * (number_of_tiles + 1)
        tile_boundaries[0] = 0
        tile_boundaries[number_of_tiles] = image_width
        for i in range(1, number_of_tiles):
            tile_boundaries[i] = i * self.total_tile_width - cumulative_border[2 * i - 1]

        result: List[Tile1d] = []
        for k in range(0, number_of_tiles):
            left_most_tile_pixel = tile_boundaries[k]
            width = tile_boundaries[k + 1] - tile_boundaries[k]
            total_border = self.total_tile_width - width

            if k == 0:
                left_border = 0
            elif k == number_of_tiles - 1:
                left_border = total_border
            else:
                left_border_index = 2 * k
                left_border = cumulative_border[left_border_index] - cumulative_border[left_border_index - 1]

                # Some assertions. These can be removed without harm.
                right_border1 = total_border - left_border
                right_border2 = cumulative_border[left_border_index + 1] - cumulative_border[left_border_index]
                if right_border1 != right_border2:
                    raise AssertionError("right_border1 != right_border2")
                if right_border1 < self.min_border_width:
                    raise AssertionError("right border < self.min_border_width")
                if left_border < self.min_border_width:
                    raise AssertionError("left border < self.min_border_width")

            right_border = total_border - left_border

            if left_border + width + right_border != self.total_tile_width:
                raise AssertionError("LB + W + RB != Total Width")

            result.append(Tile1d(left_most_tile_pixel, width, left_border, right_border))

        return result
