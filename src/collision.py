# Implementations of collision functions using numpy
import numpy as np


def segment_intersections(line: list, line_arr: np.array) -> np.array:
    """
    Return points of intersection if they exist. Leave the other points at np.NaN
    :param line: Line to find collisions of other lines with
    :param line_arr: N lines in a 4xN matrix
    :return: 2xN matrix containing
    """
    # Intersection given infinite lines. Returned in the shape 2xN where both values are NaN if there is no intersection
    # Elements are NaN if no intersection exists (e.g. the lines are parallel)
    p: np.array = _intersection(line, line_arr)

    # If any of the intersection coordinates are too big, set to NaN.
    p[~np.isnan(p) & np.any(np.abs(p) > 1e5, axis=0)] = np.NaN

    # Check that intersections are within the bounds of the main line and the other line
    # First, make rectangular regions for each line, (xmin, xmax, ymin, ymax) as rows, lines as columns
    main_region = (min(line[0:2]), max(line[0:2]), min(line[2:4]), max(line[2:4]))
    other_regions = np.vstack((np.min(line_arr[0:2], axis=0), np.max(line_arr[0:2], axis=0),
                               np.min(line_arr[2:4], axis=0), np.max(line_arr[2:4], axis=0)))

    # TODO: Increase size of boxes if too small (horizontal line)

    present_mask = ~np.isnan(p[0])
    present = p[:, present_mask]
    other_regions = other_regions[:, present_mask]

    print(present.shape, other_regions.shape)

    present[:, (present[0] < main_region[0]) | (present[0] > main_region[1]) |  # Not within main x
               (present[1] < main_region[2]) | (present[1] > main_region[3]) |  # Not within main y
               (present[0] < other_regions[0]) | (present[0] > other_regions[1]) |  # Not within other x
               (present[1] < other_regions[2]) | (present[1] > other_regions[3])  # Not within other y
    ] = np.NaN
    p[:, present_mask] = present

    return p


def _intersection(line: list, line_arr: np.array) -> np.array:
    line_slope, line_int = _line_slope_intercept(line)
    slope_int = _slope_and_intercept(line_arr)

    intersections = np.full(fill_value=np.inf, shape=(2, line_arr.shape[1]))

    # Find when the main line or the other lines are vertical
    line_vertical = line_slope is None
    other_vertical = np.isnan(slope_int[0])

    # All elements that have been dealt with
    dealt = np.full(shape=intersections.shape[1], fill_value=False)

    # Lines are parallel, don't need to handle this case
    parallel = line_slope == slope_int[0]
    intersections[:, parallel] = np.NaN
    dealt |= parallel

    # No vertical lines, use traditional formula
    no_vert = ~((line_slope is None) | np.isnan(slope_int[0]))
    no_vert_slope_int = slope_int[:, no_vert]

    x = (line_int - no_vert_slope_int[1]) / (line_slope - no_vert_slope_int[0])
    y = (line_slope * x + line_int)
    intersections[:, no_vert] = np.vstack((x, y))
    dealt |= no_vert

    # Can now assume that one of the lines are vertical.
    if line_slope is None:
        # Main line is vertical
        x = line[0]
        y = slope_int[0, ~dealt] * x + line_int
        intersections[:, ~dealt] = np.vstack((np.full(fill_value=x, shape=np.sum(~dealt)), y))
    else:
        # Other lines are vertical
        x = line_arr[0, ~dealt]
        y = line_slope * x
        intersections[:, ~dealt] = np.vstack((x, y))

    intersections[intersections == np.inf] = np.NaN
    return intersections


def _slope_and_intercept(lines: np.array):
    """
    Takes in 4xN array of lines, and outputs 2xN array of slope, intercept
    :param lines(nd.array): Array of lines
    :return: nd.array
    """
    si = np.full(shape=(2, lines.shape[1]), fill_value=np.NaN)
    not_nan_mask = lines[0] != lines[2]
    not_nan = lines[:, not_nan_mask]

    # Calculate slope and intercept
    slope = (not_nan[3] - not_nan[1]) / (not_nan[2] - not_nan[0])
    intercept = not_nan[1] - slope * not_nan[0]

    si[:, not_nan_mask] = np.vstack((slope, intercept))
    return si


def _line_slope_intercept(line: list):
    if line[0] == line[2]:
        # Infinite slope
        return None, None
    else:
        slope = (line[3] - line[1]) / (line[2] - line[0])
        return slope, line[1] - slope * line[0]
