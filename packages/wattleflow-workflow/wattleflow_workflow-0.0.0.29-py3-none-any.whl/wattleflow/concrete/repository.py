# Module Name: concrete/repository.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2024 WattleFlow
# License: Apache 2 Licence
# Description: This modul contains repository classes.

from abc import ABC
from logging import Handler, NOTSET
from typing import Generic, Optional
from wattleflow.core import IRepository, IStrategy, ITarget, T, C
from wattleflow.constants.enums import Event
from wattleflow.concrete import Attribute, AuditLogger, _NC


class GenericRepository(IRepository, Generic[T], Attribute, AuditLogger, ABC):
    def __init__(
        self,
        strategy_write: IStrategy,
        strategy_read: Optional[IStrategy] = None,
        allowed: Optional[list] = None,
        level: int = NOTSET,
        handler: Optional[Handler] = None,
        *args,
        **kwargs,
    ):
        IRepository.__init__(self)
        AuditLogger.__init__(self, level=level, handler=handler)

        # self.evaluate(strategy_read, IStrategy)
        self.evaluate(strategy_write, IStrategy)

        self._counter: int = 0
        self._strategy_read = strategy_read
        self._strategy_write = strategy_write
        self._allowed = allowed

        self.debug(
            msg=Event.Constructor.value,
            strategy_read=self._strategy_read,
            strategy_write=self._strategy_write,
            allowed=allowed,
        )

        self.configure(**kwargs)

        self.debug(msg=Event.Constructor.value, status="finalised")

    @property
    def count(self) -> int:
        return self._counter

    def clear(self) -> None:
        self.debug(msg=Event.Cleaning.value)
        self._counter = 0

    def configure(self, **kwargs):
        self.allowed(self._allowed, **kwargs)

        for name, value in kwargs.items():
            if isinstance(value, (bool, dict, list, str)):
                self.push(name, value)
                self.debug(msg=Event.Configuring.value, name=name, value=value)
            else:
                error = f"{_NC(value)}) is restricted type. [bool, dict, list, str]"
                self.error(msg=error, name=name)
                raise AttributeError(error)

    def read(self, identifier: str, item: ITarget, **kwargs) -> T:
        if not self._strategy_read:
            self.warning(msg="Missing:self._strategy_read")
            return None

        self.debug(
            Event.Reading.value,
            id=identifier,
            item=item.identifier,
            kwargs=kwargs,
        )
        self.evaluate(item, ITarget)

        document = self._strategy_read.read(
            caller=self,
            item=item,
            identifier=identifier,
            **kwargs,
        )
        self.evaluate(document, ITarget)

        self.debug(
            msg=Event.Retrieved.value,
            id=item.identifier,
            success=True,
            document=document,
        )
        return document

    def write(self, item: ITarget, caller: C, **kwargs) -> bool:
        try:
            self.evaluate(item, ITarget)
            self._counter += 1
            self.debug(
                msg=Event.Storing.value,
                counter=self._counter,
                id=item.identifier,
                caller=caller.name,
                item=item,
            )
            return self._strategy_write.write(
                caller=caller, item=item, repository=self, **kwargs
            )
        except Exception as e:
            error = f"[{self.__class__.__name__}] Write strategy failed: {e}"
            self.exception(msg=error, counter=self._counter)
            raise RuntimeError(error)
