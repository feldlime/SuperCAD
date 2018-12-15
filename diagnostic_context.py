import sys
from timeit import default_timer as timer
from typing import Optional
from uuid import UUID, uuid4
from functools import wraps
from collections import defaultdict


class DiagnosticContext:
    def __init__(self, title: str = None, file=None):
        self._identity = uuid4()
        self._title = title
        self._levels = [self._identity]
        self._level_names = [title or 'root']
        self._file = file or sys.stderr

    def _log(self, message: str):
        print(f'{" | ".join(self._level_names)} | {message}', file=self._file, flush=False)

    def __enter__(self):
        self._log(f'Diagnostic context started')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._log(f'Diagnostic context stopped')

    def _start_step(self, step_name: str, step_identity: UUID):
        self._levels.append(step_identity)
        self._level_names.append(step_name)
        self._log('started')

    def _stop_step(
        self, step_name: str, step_identity: UUID, elapsed_seconds: float
    ):
        self._log(f'stopped | {elapsed_seconds}')

        last_step_name = self._level_names.pop()
        last_step_identity = self._levels.pop()
        if last_step_identity != step_identity:
            raise ValueError(
                f"expected step '{step_name}'[{step_identity}]"
                f" does not match "
                f"actual step '{last_step_name}'[{last_step_identity}]"
            )

    def measure(self, step_name: str):
        return _Measurer(self, step_name)


class DiagnosticContextTotal(DiagnosticContext):
    def __init__(self, title: str = None, file=None):
        super().__init__(title=title, file=file)
        self._times = defaultdict(float)
        self._counts = defaultdict(int)

    def _log(self, message: str):
        pass

    def _stop_step(
        self, step_name: str, step_identity: UUID, elapsed_seconds: float
    ):
        super()._stop_step(step_name, step_identity, elapsed_seconds)
        current_full_name = ' | '.join(self._level_names + [step_name])
        self._times[current_full_name] += elapsed_seconds
        self._counts[current_full_name] += 1

    def get_times(self):
        return self._times, self._counts


class _Measurer:
    def __init__(self, context: DiagnosticContext, name: str):
        self._name = name
        self._context = context

    def __enter__(self):
        self._start_time = timer()
        self._uuid = uuid4()
        self._context._start_step(self._name, self._uuid)

    def __exit__(self, exc_type, exc_value, traceback):
        end_time = timer()
        self._context._stop_step(
            self._name, self._uuid, end_time - self._start_time
        )


DEFAULT_CONTEXT = DiagnosticContext()
DEFAULT_CONTEXT_TOTAL = DiagnosticContextTotal()


def measured(
    _func=None, *, diagnostic_context: Optional[DiagnosticContext] = None
):
    """Decorator."""

    def measure_decorator(some_function):
        actual_context = diagnostic_context or DEFAULT_CONTEXT

        @wraps(some_function)
        def wrapper(*args, **kwargs):
            with actual_context.measure(some_function.__name__):
                return some_function(*args, **kwargs)

        return wrapper

    if _func is not None:
        # measure call
        return measure_decorator(_func)
    else:
        return measure_decorator


measure = DEFAULT_CONTEXT.measure
measure_total = DEFAULT_CONTEXT_TOTAL.measure


def measured_total(_func=None):
    return measured(_func, diagnostic_context=DEFAULT_CONTEXT_TOTAL)


if __name__ == '__main__':
    from restrictions import SegmentsNormal, SegmentsSpotsJoint
    from project import CADProject
    from figures import Segment
    from bindings import choose_best_bindings

    with measure('create project'):
        project = CADProject()

    with measure('create figures'):
        segment1 = Segment((0, 0), 0, 10)
        segment1_name = project.add_figure(segment1)
        segment2 = Segment((1, 1), 1, 10)
        segment2_name = project.add_figure(segment2)
        # segment3 = Segment((2, 5), -1, 10)
        # segment3_name = project.add_figure(segment3)

    with measure('choose binding'):
        bb = choose_best_bindings(project.bindings, 10, 0)[0]  # end of segment 1

    with measure('add restrictions'):
        project.add_restriction(SegmentsNormal(), (segment1_name, segment2_name))
        project.add_restriction(SegmentsSpotsJoint('start', 'start'), (segment1_name, segment2_name))
        # project.add_restriction(SegmentsNormal(), (segment2_name, segment3_name))

    with measure('move segment 1 end'):
        project.move_figure(bb, 10 + 1, 0)
