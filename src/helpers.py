from pygame.transform import rotate


def vec_len(vector):
    return sum((i ** 2 for i in vector))


def make_len(vector, target_length):
    l = vec_len(vector)
    for i in range(len(vector)):
        vector[i] *= target_length / l


def normalize(vector):
    l = vec_len(vector)
    for i in range(len(vector)):
        vector[i] /= l


def add_to(vec_to, vec_from):
    for i in range(len(vec_to)):
        vec_to[i] += vec_from[i]

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
