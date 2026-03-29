#!/usr/bin/env python3
"""event_emitter - Event emitter with once, wildcard, and priority listeners."""
import sys
from collections import defaultdict

class EventEmitter:
    def __init__(self):
        self._listeners = defaultdict(list)
        self._once = set()
    def on(self, event, fn, priority=0):
        self._listeners[event].append((priority, fn))
        self._listeners[event].sort(key=lambda x: -x[0])
    def once(self, event, fn, priority=0):
        self._once.add((event, id(fn)))
        self.on(event, fn, priority)
    def off(self, event, fn=None):
        if fn is None:
            self._listeners[event] = []
        else:
            self._listeners[event] = [(p, f) for p, f in self._listeners[event] if f is not fn]
    def emit(self, event, *args, **kwargs):
        results = []
        to_remove = []
        for priority, fn in self._listeners.get(event, []):
            results.append(fn(*args, **kwargs))
            if (event, id(fn)) in self._once:
                to_remove.append((event, fn))
                self._once.discard((event, id(fn)))
        # wildcard
        for priority, fn in self._listeners.get("*", []):
            results.append(fn(event, *args, **kwargs))
        for ev, fn in to_remove:
            self.off(ev, fn)
        return results
    def listener_count(self, event):
        return len(self._listeners.get(event, []))

def test():
    ee = EventEmitter()
    log = []
    ee.on("data", lambda x: log.append(f"a:{x}"))
    ee.on("data", lambda x: log.append(f"b:{x}"), priority=10)
    ee.emit("data", 42)
    assert log == ["b:42", "a:42"]  # priority order
    # once
    once_log = []
    ee.once("ping", lambda: once_log.append(1))
    ee.emit("ping")
    ee.emit("ping")
    assert once_log == [1]
    # wildcard
    wild = []
    ee.on("*", lambda event, *a: wild.append(event))
    ee.emit("foo")
    assert "foo" in wild
    # off
    ee.off("data")
    assert ee.listener_count("data") == 0
    print("OK: event_emitter")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: event_emitter.py test")
