"""The tiling.py module implements a function called 'tile_image' which slices images into smaller 
pieces called 'tiles'. This is used to improve the accuracy and memory efficiency of object
detection models that need to detect very small objects in high resolution images.
"""

from PIL import Image
from typing import List, Tuple
import math


def tile_image(
    image: Image.Image,
    slice_width: int,
    slice_height: int,
    horizontal_overlap_ratio: float,
    vertical_overlap_ratio: float,
) -> List[Image.Image]:
    """Splits a larger image into smaller 'tiles'.

    In the likely event that the exact choices of overlap ratios and slice dimensions do not
    multiply to make exactly the image's dimensions, the image.crop method pads the image with
    black on the right and bottom sides.

    Args:
        `image` (PIL Image): The image to tile.
        `slice_height` (int): The height of each slice.
        `slice_width` (int): The width of each slice.
        `horizontal_overlap_ratio` (float) - The amount of left-right overlap between slices.
        `vertical_overlap_ratio` (float) - The amount of top-bottom overlap between slices.

    Returns: A list of sliced images.
    """
    validate_tile_parameters(
        image,
        slice_width,
        slice_height,
        horizontal_overlap_ratio,
        vertical_overlap_ratio,
    )
    image_width, image_height = image.size
    tile_coordinates: List[Tuple[int]] = generate_tile_coordinates(
        image_width,
        image_height,
        slice_width,
        slice_height,
        horizontal_overlap_ratio,
        vertical_overlap_ratio,
    )
    images: List[Image.Image] = [
        [image.crop(box) for box in tc] for tc in tile_coordinates
    ]
    return images


def validate_tile_parameters(
    image: Image.Image,
    slice_width: int,
    slice_height: int,
    horizontal_overlap_ratio: float,
    vertical_overlap_ratio: float,
) -> None:
    """Validates the parameters for the function 'tile_image'.

    Args:
        `image` (PIL Image) - The image to tile.
        `slice_height` (int) - The height of each slice.
        `slice_width` (int) - The width of each slice.
        `horizontal_overlap_ratio` (float) - The amount of left-right overlap between slices.
        `vertical_overlap_ratio` (float) - The amount of top-bottom overlap between slices.

    Raises:
        ValueError: If slice_width is not within (0, image_width], slice_height not within (0, image_height), or horizontal/vertical overlap ratio not in (0, 1].
    """
    if not 0 < slice_width <= image.size[0]:
        raise ValueError(
            f"slice_width must be between 1 and the image's width (slice_width passed was {slice_width})."
        )
    if not 0 < slice_height <= image.size[1]:
        raise ValueError(
            f"slice_height must be between 1 and the image's height (slice_height passed was {slice_height})."
        )
    if not 0 < horizontal_overlap_ratio <= 1:
        raise ValueError(
            f"horizontal_overlap_ratio must be greater than 0 and less than or equal to 1 (horizontal_overlap_ratio passed was {horizontal_overlap_ratio}."
        )
    if not 0 < vertical_overlap_ratio <= 1:
        raise ValueError(
            f"vertical_overlap_ratio must be greater than 0 and less than or equal to 1 (vertical_overlap_ratio passed was {vertical_overlap_ratio}."
        )


def generate_tile_coordinates(
    image_width: int,
    image_height: int,
    slice_width: int,
    slice_height: int,
    horizontal_overlap_ratio: int,
    vertical_overlap_ratio: int,
) -> List[List[Tuple[int]]]:
    """Generates the box coordinates of the tiles for the function 'tile_image'.

    Args:
        `image_width` (int): The image's width.
        `image_height` (int): The image's height.
        `slice_height` (int): The height of each slice.
        `slice_width` (int): The width of each slice.
        `horizontal_overlap_ratio` (float): The amount of left-right overlap between slices.
        `vertical_overlap_ratio` (float): The amount of top-bottom overlap between slices.

    Returns: A 2d list of four coordinate tuples encoding the left, top, right, and bottom of each tile.
    """
    tile_coords = [
        [
            (
                x * round(slice_width * horizontal_overlap_ratio),
                y * round(slice_width * vertical_overlap_ratio),
                slice_width + x * round(slice_width * horizontal_overlap_ratio),
                slice_height + y * round(slice_width * vertical_overlap_ratio),
            )
            for x in range(
                math.floor(image_width / (slice_width * horizontal_overlap_ratio))
            )
        ]
        for y in range(
            math.floor(image_height / (slice_height * vertical_overlap_ratio))
        )
    ]
    return tile_coords


def tile_annotations(
    annotations: List,
    image_width: int,
    image_height: int,
    slice_width: int,
    slice_height: int,
    horizontal_overlap_ratio: float,
    vertical_overlap_ratio: float,
):
    """Tiles image annotations based on a specified grid pattern with overlap.

    This function takes a list of annotations (any annotation that implements the 'box' property)
    representing objects within an image, and divides the image into a grid of tiles
    with a specified size and overlap. It then assigns each annotation to the tile(s)
    based on whether the annotation fully fits into the tile.

    Args:
        `annotations` (List): A list of annotations (anything that implements the 'box' property).
        `image_width` (int): The width of the image in pixels.
        `image_height` (int): The height of the image in pixels.
        `slice_width` (int): The width of each tile in pixels.
        `slice_height` (int): The height of each tile in pixels.
        `horizontal_overlap_ratio` (float): The ratio (0.0 to 1.0) of the tile width that overlaps
            horizontally between adjacent tiles.
        `vertical_overlap_ratio` (float): The ratio (0.0 to 1.0) of the tile height that overlaps
            vertically between adjacent tiles.

    Returns:
        A list of lists, where each sub-list represents a tile in the grid. Each tile's
        sub-list contains the annotations that intersect fully with that specific tile.
    """
    tile_coordinates: List[List[Tuple[int]]] = generate_tile_coordinates(
        image_width,
        image_height,
        slice_width,
        slice_height,
        horizontal_overlap_ratio,
        vertical_overlap_ratio,
    )
    annotation_tiles = [
        [get_annotations_in_tile(annotations, tc) for tc in tc_list]
        for tc_list in tile_coordinates
    ]
    return annotation_tiles


def get_annotations_in_tile(annotations: List, tile: Tuple[int]) -> List:
    """ """
    annotation_in_tile = lambda ann, tile: all(
        [
            ann.box[0] >= tile[0],
            ann.box[1] >= tile[1],
            ann.box[2] <= tile[2],
            ann.box[3] <= tile[3],
        ]
    )
    annotations_in_tile: List = list(
        filter(lambda ann: annotation_in_tile(ann, tile), annotations)
    )
    return annotations_in_tile
