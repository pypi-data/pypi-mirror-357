import functools
from collections.abc import Callable, Iterable, Sequence
from typing import Any, overload

from ._base import Callback, TimerRecords
from ._function import TimedFunction
from ._iterable import TimedIterable
from ._timer import Timer


@functools.singledispatch
def _timer_dispatch(_: Any, /, *_args, **_kwargs) -> Any:
    raise TypeError


@_timer_dispatch.register(str)
def _(name: str, /, **kwargs) -> Timer:
    return Timer(name=name, **kwargs)


@_timer_dispatch.register(Callable)  # pyright: ignore[reportArgumentType, reportCallIssue]
def _(fn: Callable, /, **kwargs) -> TimedFunction:
    return TimedFunction(fn, timing=TimerRecords(**kwargs))


@_timer_dispatch.register(Iterable)
def _(iterable: Iterable, /, *, total: int | None = None, **kwargs) -> TimedIterable:
    return TimedIterable(iterable, timing=TimerRecords(**kwargs), total=total)


@overload
def timer[**P, T](
    name: str | None = None,
    *,
    timers: Sequence[str] = ("perf",),
    cb_finish: Callback | None = None,
    cb_start: Callback | None = None,
    cb_stop: Callback | None = None,
) -> Timer: ...
@overload
def timer[**P, T](
    fn: Callable[P, T],
    /,
    *,
    name: str | None = None,
    timers: Sequence[str] = ("perf",),
    cb_finish: Callback | None = None,
    cb_start: Callback | None = None,
    cb_stop: Callback | None = None,
) -> TimedFunction[P, T]: ...
@overload
def timer[**P, T](
    iterable: Iterable[T],
    /,
    *,
    name: str | None = None,
    timers: Sequence[str] = ("perf",),
    total: int | None = None,
    cb_finish: Callback | None = None,
    cb_start: Callback | None = None,
    cb_stop: Callback | None = None,
) -> TimedIterable[T]: ...
def timer(*args, **kwargs) -> Any:
    if args:
        return _timer_dispatch(*args, **kwargs)
    return Timer(*args, **kwargs)
