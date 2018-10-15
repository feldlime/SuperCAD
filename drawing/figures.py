from geometry.figures import Point, Segment


class Drawable:
    pass


class DrawnPoint(Point, Drawable):
    pass


class DrawnSegment(Segment, Drawable):
    pass
