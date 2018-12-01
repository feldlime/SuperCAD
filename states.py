class ChooseSt:
    NOTHING = 0
    CHOOSE = 1

class ControllerWorkSt:
    NOTHING = 0
    ADD_POINT = 1
    ADD_SEGMENT = 2
    RESTR_FIXED = 3
    RESTR_POINT_ON_SEGMENT = 4
    RESTR_JOINT = 5
    RESTR_SEGMENT_ANGLE_FIXED = 6
    RESTR_SEGMENT_HORIZONTAL = 7
    RESTR_SEGMENT_LENGTH_FIXED = 8
    RESTR_SEGMENTS_NORMAL = 9
    RESTR_SEGMENTS_PARALLEL = 10

    # def __init__(self):
    #     self._state = self.NOTHING
    #
    # def __get__(self, instance, owner):
    #
    #
    # def is_restr(self):


class ControllerSt:
    HIDE = 0
    SHOW = 1
    SUBMIT = 2
    ADD = 3
    MOUSE_ADD = 4
