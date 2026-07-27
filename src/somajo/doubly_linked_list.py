#!usr/bin/env python3
"""Doubly linked list implementation for SoMaJo tokenization."""

from __future__ import annotations

import operator
from typing import Any, Callable, Generator, Iterable, TypeVar

T = TypeVar('T')


class DLLElement:
    """A node in a doubly linked list.

    Args:
        val: Value stored in the element. Defaults to None.
        prv: Previous element in the list. Defaults to None.
        nxt: Next element in the list. Defaults to None.
        lst: The DLL this element belongs to. Defaults to None.

    """

    def __init__(
        self,
        val: Any = None,
        prv: DLLElement | None = None,
        nxt: DLLElement | None = None,
        lst: DLL | None = None
    ) -> None:
        if isinstance(val, DLLElement):
            val = val.value
        self.prev: DLLElement | None = prv
        self.next: DLLElement | None = nxt
        self.value: Any = val
        self.list: DLL | None = lst
        if prv is not None:
            prv.next = self
        if nxt is not None:
            nxt.prev = self


class DLL:
    """Doubly linked list data structure.

    Args:
        iterable: Initial items to add to the list. Defaults to None.

    """

    def __init__(self, iterable: Iterable[T] | None = None) -> None:
        self.first: DLLElement | None = None
        self.last: DLLElement | None = None
        self.size: int = 0
        if iterable is not None:
            self.extend(iterable)

    def __iter__(self, start: DLLElement | None = None) -> Generator[DLLElement, None, None]:
        current: DLLElement | None = self.first
        if start is not None:
            current = start
        while current is not None:
            yield current
            current = current.next

    def __reversed__(self, start: DLLElement | None = None) -> Generator[DLLElement, None, None]:
        current: DLLElement | None = self.last
        if start is not None:
            current = start
        while current is not None:
            yield current
            current = current.prev

    def __len__(self) -> int:
        return self.size

    def __str__(self) -> str:
        return str(self.to_list())

    def _find_matching_element(
        self,
        item: DLLElement,
        attrgetter: Callable[[DLLElement], Any],
        value: Any,
        ignore_attrgetter: Callable[[DLLElement], Any] | None = None,
        ignore_value: Any = None,
        forward: bool = True
    ) -> DLLElement | None:
        current: DLLElement | None = item
        direction = operator.attrgetter("next")
        if not forward:
            direction = operator.attrgetter("prev")
        while direction(current) is not None:
            current = direction(current)
            if ignore_attrgetter is not None:
                if ignore_attrgetter(current) == ignore_value:
                    continue
            if attrgetter(current) == value:
                return current
        return None

    def append(self, item: T) -> None:
        element = DLLElement(item, self.last, None, self)
        if self.first is None:
            self.first = element
        self.last = element
        self.size += 1

    def append_left(self, item: T) -> None:
        element = DLLElement(item, None, self.first, self)
        if self.last is None:
            self.last = element
        self.first = element
        self.size += 1

    def extend(self, iterable: Iterable[T]) -> None:
        for item in iterable:
            self.append(item)

    def insert_left(self, item: T, ref_element: DLLElement) -> None:
        element = DLLElement(item, ref_element.prev, ref_element, self)
        ref_element.prev = element
        if self.first is ref_element:
            self.first = element
        self.size += 1

    def insert_right(self, item: T, ref_element: DLLElement) -> None:
        element = DLLElement(item, ref_element, ref_element.next, self)
        ref_element.next = element
        if self.last is ref_element:
            self.last = element
        self.size += 1

    def is_left_of(self, element: DLLElement, ref_element: DLLElement) -> bool:
        current: DLLElement = ref_element
        while current is not self.first:
            assert isinstance(current.prev, DLLElement)  # for mypy
            current = current.prev
            if current is element:
                return True
        return False

    def is_right_of(self, element: DLLElement, ref_element: DLLElement) -> bool:
        return self.is_left_of(ref_element, element)

    def next_matching(
        self,
        item: DLLElement,
        attrgetter: Callable[[DLLElement], Any],
        value: Any,
        ignore_attrgetter: Callable[[DLLElement], Any] | None = None,
        ignore_value: Any = None
    ) -> DLLElement | None:
        return self._find_matching_element(item, attrgetter, value, ignore_attrgetter, ignore_value, forward=True)

    def pop(self) -> Any:
        if self.size == 0:
            raise IndexError
        assert isinstance(self.last, DLLElement)  # for mypy
        element: DLLElement = self.last
        self.remove(element)
        return element.value

    def previous_matching(
        self,
        item: DLLElement,
        attrgetter: Callable[[DLLElement], Any],
        value: Any,
        ignore_attrgetter: Callable[[DLLElement], Any] | None = None,
        ignore_value: Any = None
    ) -> DLLElement | None:
        return self._find_matching_element(item, attrgetter, value, ignore_attrgetter, ignore_value, forward=False)

    def remove(self, element: DLLElement) -> None:
        if self.first is element:
            self.first = element.next
        if self.last is element:
            self.last = element.prev
        if element.prev is not None:
            element.prev.next = element.next
        if element.next is not None:
            element.next.prev = element.prev
        self.size -= 1

    def to_list(self) -> list[T]:
        return [e.value for e in self]
