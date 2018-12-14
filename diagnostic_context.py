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


class DiagnosticContextTimer(DiagnosticContext):
    def __init__(self, title: str = None, file=None):
        super().__init__(title=title, file=file)
        self._times = defaultdict(float)

    def _log(self, message: str):
        pass

    def _stop_step(
        self, step_name: str, step_identity: UUID, elapsed_seconds: float
    ):
        super()._stop_step(step_name, step_identity, elapsed_seconds)
        current_full_name = ' | '.join(self._level_names + [step_name])
        self._times[current_full_name] += elapsed_seconds

    def get_times(self):
        return self._times


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
DEFAULT_CONTEXT_TIMER = DiagnosticContextTimer()


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
measure_total = DEFAULT_CONTEXT_TIMER.measure


def measured_total(_func=None):
    return measured(_func, diagnostic_context=DEFAULT_CONTEXT_TIMER)
