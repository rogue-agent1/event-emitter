#!/usr/bin/env python3
"""Event emitter with wildcards and once listeners."""
import re

class EventEmitter:
    def __init__(self):
        self._listeners = {}
        self._once = set()

    def on(self, event: str, callback):
        self._listeners.setdefault(event, []).append(callback)
        return self

    def once(self, event: str, callback):
        self.on(event, callback)
        self._once.add((event, id(callback), callback))
        return self

    def off(self, event: str, callback=None):
        if callback is None:
            self._listeners.pop(event, None)
        elif event in self._listeners:
            self._listeners[event] = [cb for cb in self._listeners[event] if cb is not callback]

    def emit(self, event: str, *args, **kwargs):
        listeners = []
        for pattern, cbs in self._listeners.items():
            if pattern == event or (pattern.endswith("*") and event.startswith(pattern[:-1])):
                listeners.extend(cbs)
        to_remove = []
        for cb in listeners:
            cb(*args, **kwargs)
            for key in self._once:
                if key[2] is cb:
                    to_remove.append((key[0], cb))
        for ev, cb in to_remove:
            self.off(ev, cb)
            self._once = {k for k in self._once if k[2] is not cb}

    def listener_count(self, event: str) -> int:
        return len(self._listeners.get(event, []))

if __name__ == "__main__":
    ee = EventEmitter()
    ee.on("data", lambda x: print(f"Got: {x}"))
    ee.emit("data", 42)

def test():
    ee = EventEmitter()
    results = []
    ee.on("test", lambda x: results.append(x))
    ee.emit("test", 1)
    ee.emit("test", 2)
    assert results == [1, 2]
    # Once
    once_results = []
    ee.once("once", lambda x: once_results.append(x))
    ee.emit("once", "a")
    ee.emit("once", "b")
    assert once_results == ["a"]
    # Wildcard
    wild = []
    ee.on("user.*", lambda x: wild.append(x))
    ee.emit("user.login", "alice")
    ee.emit("user.logout", "bob")
    assert wild == ["alice", "bob"]
    # Off
    ee.off("test")
    ee.emit("test", 3)
    assert results == [1, 2]
    # Count
    assert ee.listener_count("user.*") == 1
    print("  event_emitter: ALL TESTS PASSED")
