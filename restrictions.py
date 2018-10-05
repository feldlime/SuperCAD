class Restriction:
    def get_restriction_equation(self, objects):
        # may be no objects
        pass


class FixedLength(Restriction):
    def __init__(self, length=None):
        """

        length:
            If None use current length.
        """
        self._length = length


# more
