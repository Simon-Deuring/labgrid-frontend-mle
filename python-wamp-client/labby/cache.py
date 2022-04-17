from abc import abstractmethod
import asyncio
import contextlib
from asyncio import CancelledError
from inspect import iscoroutinefunction
from typing import Any, Awaitable, Callable, Generic, List, TypeVar, Union
from attr import attrib, attrs


class CacheStrategy:
    def __init__(self) -> None:
        self._expired: bool = False

    @abstractmethod
    def should_refresh(self) -> bool:
        return self._expired

    @abstractmethod
    def reset(self):
        self._expired = False


class GetStrategy:
    # update on get
    @abstractmethod
    def get_action(self):
        raise NotImplementedError


class TimingStrategy:
    # update on tick
    @abstractmethod
    def stop(self):
        raise NotImplementedError


class PeriodicRefreshStrategy(CacheStrategy, TimingStrategy):
    def __init__(self, period: float):
        CacheStrategy.__init__(self)
        TimingStrategy.__init__(self)

        async def clear_in_background():
            with contextlib.suppress(CancelledError):
                while True:
                    while self._expired:
                        # too soon after last refresh
                        await asyncio.sleep(0.5)
                    await asyncio.sleep(delay=period)
                    self._expired = True

        self.clear_task = asyncio.get_event_loop().create_task(clear_in_background())

    def stop(self):
        self.clear_task.cancel()


@attrs
class CounterStrategy(CacheStrategy, GetStrategy):
    counter_default: int = attrib()
    _counter: int = 0

    def __attrs_pre_init__(self):
        CacheStrategy.__init__(self)
        GetStrategy.__init__(self)

    def __attrs_post_init__(self):
        self._counter = self.counter_default

    def get_action(self):
        self._counter -= 1
        if self._counter <= 0:
            self._expired = True

    def reset(self):
        self._expired = False
        self._counter = self.counter_default


T = TypeVar("T")


class Cache(Generic[T]):
    def __init__(
        self,
        data: T,
        refresh_data: Union[Callable[[Any], T],
                            Callable[[Any], Awaitable[T]]] = attrib(),
        strategies: List[CacheStrategy] = attrib(),
    ):
        self._data = data
        self.refresh_data = refresh_data
        self.strategies = strategies
        if hasattr(self._data, "__getitem__"):

            def __getitem__(self, ind: Any) -> T:
                return self.get()[ind]

            self.__getitem__ = __getitem__
        self.get = self.make_get(iscoroutinefunction(refresh_data))

        if hasattr(self._data, "__contains__"):
            def __contains__(self, key):
                return key in self._data
            self.__contains__ = __contains__

        if hasattr(self._data, "__setitem__"):
            def __setitem__(self, key, entry):
                self._data[key] = entry
            self.__setitem__ = __setitem__

    def stop(self):
        for strat in self.strategies:
            if isinstance(strat, TimingStrategy):
                strat.stop()
        self.get = lambda: self._data  # type: ignore
        self.strategies.clear()

    def __delitem__(self, index):
        del self._data[index]  # type: ignore

    def get_soft(self) -> T:
        # access data without refreshing cache
        return self._data

    def make_get(self, isasync: bool):
        def get(*args) -> T:
            # TODO could we optimize this?
            for strat in self.strategies:
                if isinstance(strat, GetStrategy):
                    strat.get_action()
            reset_strats = False
            if self._data is None:
                self._data = self.refresh_data(*args)
            else:
                for strat in self.strategies:
                    if strat.should_refresh():
                        self._data = self.refresh_data(*args)
                        reset_strats = True
                        break
                if reset_strats:
                    for strat in self.strategies:
                        strat.reset()
            return self._data  # type: ignore

        async def get_async(*args) -> T:
            # TODO could we optimize this?
            for strat in self.strategies:
                if isinstance(strat, GetStrategy):
                    strat.get_action()
            reset_strats = False
            if self._data is None:
                self._data = await self.refresh_data(*args)
            else:
                for strat in self.strategies:
                    if strat.should_refresh():
                        self._data = await self.refresh_data(*args)
                        reset_strats = True
                        break
                if reset_strats:
                    for strat in self.strategies:
                        strat.reset()
            return self._data  # type: ignore

        return get_async if isasync else get
