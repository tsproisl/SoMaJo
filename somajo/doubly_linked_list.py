#!/usr/bin/env python3


class DLLNode:
    def __init__(self, val=None, prv=None, nxt=None, lst=None):
        if isinstance(val, DLLNode):
            val = val.val
        self.prev = prv
        self.next = nxt
        self.value = val
        self.list = lst
        if prv is not None:
            prv.next = self
        if nxt is not None:
            nxt.prev = self


class DLL:
    def __init__(self, iterable=None):
        self.first = None
        self.last = None
        self.size = 0
        self.last_access_node = None
        self.last_access_idx = -1
        if iterable is not None:
            self.extend(iterable)

    def __iter__(self):
        current = self.first
        while current is not None:
            yield current
            current = current.next

    def __len__(self):
        return self.size

    def __str__(self):
        return str(self.to_list())

    def append(self, item):
        node = DLLNode(item, self.last, None, self)
        if self.first is None:
            self.first = node
        self.last = node
        self.size += 1

    def extend(self, iterable):
        for item in iterable:
            self.append(item)

    def insert_left(self, item, ref_node):
        node = DLLNode(item, ref_node.prev, ref_node, self)
        ref_node.prev = node
        if self.first is ref_node:
            self.first = node
        self.size += 1

    def to_list(self):
        return [e.value for e in self]

    def remove(self, node):
        if self.first is node:
            self.first = node.next
        if self.last is node:
            self.last = node.prev
        if node.prev is not None:
            node.prev.next = node.next
        if node.next is not None:
            node.next.prev = node.prev
        self.size -= 1
