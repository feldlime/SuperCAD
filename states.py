class ControllerWorkSt:
    NOTHING = 0
    ADD_POINT = 1
    ADD_SEGMENT = 2
    RESTR_JOINT = 3
    RESTR_POINT_ON_SEGMENT_LINE = 4
    RESTR_SEGMENTS_PARALLEL = 5
    RESTR_SEGMENTS_NORMAL = 6
    RESTR_SEGMENT_VERTICAL = 7
    RESTR_SEGMENT_HORIZONTAL = 8
    RESTR_FIXED = 9
    RESTR_SEGMENT_LENGTH_FIXED = 10
    RESTR_SEGMENT_ANGLE_FIXED = 11
    RESTR_SEGMENT_ANGLE_BETWEEN_FIXED = 12

    @staticmethod
    def is_restr(st):
        return 3 <= st <= 12


class CreationSt:
    NOTHING = 0
    POINT_SET = 1
    SEGMENT_START_SET = 2
    SEGMENT_END_SET = 3


class ActionSt:
    NOTHING = 0
    BINDING_PRESSED = 1
    MOVE = 2


class ControllerCmd:
    HIDE = 0
    SHOW = 1
    STEP = 2
    SUBMIT = 3
    MOVE = 4



