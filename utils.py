class IncorrectParamError(Exception):
    pass


class IncorrectParamType(IncorrectParamError, TypeError):
    pass


class IncorrectParamValue(IncorrectParamError, ValueError):
    pass


def validate_num(value, parameter_name):
    if not (isinstance(value, int) or isinstance(value, float)):
        raise IncorrectParamType(f'Incorrect type of {parameter_name}')


def validate_positive_num(value, parameter_name):
    validate_num(value, parameter_name)
    if value <= 0:
        raise IncorrectParamValue(f'{parameter_name.capitalize()} '
                                  f'must be positive')


def validate_coordinates(coordinates, msg):
    if not isinstance(coordinates, tuple) \
            or len(coordinates) != 2 \
            or not (isinstance(coordinates[0], int) or
                    isinstance(coordinates[0], float)) \
            or not (isinstance(coordinates[1], int) or
                    isinstance(coordinates[1], float)):
        raise IncorrectParamError(msg)
