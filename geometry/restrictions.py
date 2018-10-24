"""Module with classes of geometry restrictions."""
import

class Restriction:
    def get_restriction_equation(self, **kwargs):
        # may be no objects
        raise NotImplementedError


class FixedLength(Restriction):
    def __init__(self, length):
        """

        length:
            If None use current length.
        """
        self._length = length

    def get_restriction_equation(self, name_segment):



# more
