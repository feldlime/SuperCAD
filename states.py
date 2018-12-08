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


class ControllerSt:
    HIDE = 0
    SHOW = 1
    SUBMIT = 2
    ADD = 3
    MOUSE_ADD = 4
    MOVE = 5


class CreationSt:
    NOTHING = 0
    POINT_SET = 1
    SEGMENT_START_SET = 2
    SEGMENT_END_SET = 3
    MOVE = 4


