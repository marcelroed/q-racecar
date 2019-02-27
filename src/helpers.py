from pygame.transform import rotate


def vec_len(vector):
    return sum((i ** 2 for i in vector))

def _intersection(l1, l2):
    """
    Returns point of intersection for infinite lines or None, depending on if it exists or not. If lines are parallel,
    it returns none.
    :param l1: Line no. 1, of format [(x1, y1), (x2, y2)]
    :param l2: Line no. 2
    :return: None if no point, (xi, yi) otherwise
    """
    s1, i1 = _slope_and_intercept(l1)
    s2, i2 = _slope_and_intercept(l2)

    if s1 == s2:
        # Lines are parallel, don't need to handle this case
        return None

    if s1 is not None and s2 is not None:
        # No vertical lines, use traditional formula
        x = (i1 - i2) / (s2 - s1)
        y = s1 * x + i1
        return x, y

    # Can now assume that exactly one is vertical
    if s1 is None:
        # Line 1 is vertical
        x = l1[0][0]
        y = s2 * x
        return x, y

    # Line 2 is vertical
    x = l2[0][0]
    y = s1 * x
    return x, y


def _slope_and_intercept(line):
    p1, p2 = line
    if p1[0] == p2[0]:
        # Infinite slope
        return None, None
    else:
        slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
        return slope, p1[1] - slope * p1[0]

def rot_center(image, rect, angle):
    """rotate an image while keeping its center"""
    rot_image = rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image, rot_rect
