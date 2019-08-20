import numpy as np

from src.collision import _intersection
from src.helpers import _intersection as single_int


def test_intersections():
    print('testing intersection code')
    line1 = [1, 1, 2, 2]
    line2 = np.array([1, 2, 2, 1]).reshape(4, 1)
    print(f'intersection: {_intersection(line1, line2)}')
    assert False


def test_intersection():
    print('testing single intersection code')
    line1 = [[1, 1], [2, 2]]
    line2 = [[1, 2], [2, 1]]
    print(f'intersection at {single_int(line1, line2)}')
    assert False
