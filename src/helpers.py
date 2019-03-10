from pygame import Rect
from pygame.math import Vector2


class Line:
    def __init__(self, p1, p2):
        self.first = p1
        self.second = p2

    def __getitem__(self, item):
        if item == 0:
            return self.first
        elif item == 1:
            return self.second
        else:
            raise IndexError()

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n >= 2:
            raise StopIteration
        res = self[self.n]
        self.n += 1
        return res


def translate_shape(shape, by_vec):
    # Assumes shapes are a list of lines
    return [translate_line(l, by_vec) for l in shape]


def translate_line(line, by_vec):
    # Assumes lines are a list of points (Vector2)
    return [point + by_vec for point in line]


def translate_point(point, by_vec):
    return point + by_vec


def rotate_shape(shape, point, angle):
    return [rotate_line(l, point, angle) for l in shape]


def rotate_line(l, p, angle):
    """
        Rotate line around point
        :param l: The line to rotate
        :param p: The point to rotate about
        :return: A new, rotated line
    """
    return list(map(lambda point: rotate_point(point, p, angle), l))


def rotate_point(point, anchor, angle):
    dist_vec = point - anchor
    return anchor + dist_vec.rotate(angle)


def segment_intersection(l1, l2):
    """
    Return point of intersection if it exists.
    :param l1: Line 1
    :param l2: Line 2
    :return: Point (x,y) if intersection exists, otherwise None
    """
    # Intersection point given infinite lines
    p = _intersection(l1, l2)
    if p is None:
        print('failed initial intersection:')
        return None

    for coord in p:
        if abs(coord) > 1e5:
            return None

    # Check that this intersection is within the boundaries of both lines
    # Rectangles represent boundaries for lines
    l1 = [i for i in l1]
    l2 = [i for i in l2]
    r1, r2 = (Rect(l[0], [l[1][i] - l[0][i] for i in range(2)]) for l in (l1, l2))
    r1.normalize()
    r2.normalize()
    for r in (r1, r2):
        r.w = max(r.w, 3)
        r.h = max(r.h, 3)
    # print(r1, r2)

    if r1.collidepoint(p) and r2.collidepoint(p):
        return p
    return None


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


if __name__ == '__main__':
    # Test intersection
    # assert segment_intersection([Vector2(0, 0), Vector2(10, 10)], (Vector2(5, 0), Vector2(0, 5))) is not None
    # assert segment_intersection(Vector2(50, 50), Vector2())
    line = Line(Vector2(1, 2), Vector2(3, 4))
    print(list(map(lambda v: "Vector: ({}, {})".format(*v), line)))
