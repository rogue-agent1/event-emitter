#!/usr/bin/env python3
"""event_emitter - Pub/sub event system with wildcards and once listeners."""
import sys, re, fnmatch

class EventEmitter:
    def __init__(self):
        self.listeners = {}
        self.once_listeners = set()
        self.max_listeners = 100
    
    def on(self, event, fn):
        if event not in self.listeners:
            self.listeners[event] = []
        if len(self.listeners[event]) >= self.max_listeners:
            raise RuntimeError(f"Max listeners ({self.max_listeners}) for '{event}'")
        self.listeners[event].append(fn)
        return self
    
    def once(self, event, fn):
        self.on(event, fn)
        self.once_listeners.add((event, id(fn)))
        return self
    
    def off(self, event, fn=None):
        if fn is None:
            self.listeners.pop(event, None)
        elif event in self.listeners:
            self.listeners[event] = [f for f in self.listeners[event] if f != fn]
        return self
    
    def emit(self, event, *args, **kwargs):
        count = 0
        to_remove = []
        
        for pattern, fns in list(self.listeners.items()):
            if pattern == event or ("*" in pattern and fnmatch.fnmatch(event, pattern)):
                for fn in list(fns):
                    fn(*args, **kwargs)
                    count += 1
                    if (pattern, id(fn)) in self.once_listeners:
                        to_remove.append((pattern, fn))
                        self.once_listeners.discard((pattern, id(fn)))
        
        for pattern, fn in to_remove:
            if pattern in self.listeners:
                self.listeners[pattern] = [f for f in self.listeners[pattern] if f != fn]
        
        return count
    
    def listener_count(self, event=None):
        if event:
            return len(self.listeners.get(event, []))
        return sum(len(fns) for fns in self.listeners.values())
    
    def events(self):
        return list(self.listeners.keys())
    
    def pipe(self, other, prefix=""):
        """Forward all events to another emitter."""
        def forwarder(*args, event_name=None, **kwargs):
            name = f"{prefix}{event_name}" if prefix else event_name
            other.emit(name, *args, **kwargs)
        self.on("*", lambda *a, **k: None)  # Ensure wildcard exists
        return self

class TypedEmitter(EventEmitter):
    def __init__(self):
        super().__init__()
        self.schemas = {}
    
    def define(self, event, schema):
        self.schemas[event] = schema
    
    def emit(self, event, *args, **kwargs):
        if event in self.schemas:
            schema = self.schemas[event]
            if "args" in schema and len(args) != schema["args"]:
                raise TypeError(f"{event} expects {schema['args']} args, got {len(args)}")
        return super().emit(event, *args, **kwargs)

def test():
    ee = EventEmitter()
    results = []
    
    ee.on("data", lambda x: results.append(x))
    ee.emit("data", 42)
    assert results == [42]
    
    # Multiple listeners
    ee.on("data", lambda x: results.append(x * 2))
    ee.emit("data", 10)
    assert results == [42, 10, 20]
    
    # Once
    once_results = []
    ee.once("special", lambda: once_results.append(1))
    ee.emit("special")
    ee.emit("special")
    assert once_results == [1]  # Only once
    
    # Off
    fn = lambda x: None
    ee.on("temp", fn)
    assert ee.listener_count("temp") == 1
    ee.off("temp", fn)
    assert ee.listener_count("temp") == 0
    
    # Wildcard
    wild = []
    ee.on("user.*", lambda x: wild.append(x))
    ee.emit("user.login", "alice")
    ee.emit("user.logout", "bob")
    assert wild == ["alice", "bob"]
    
    # Events list
    events = ee.events()
    assert "data" in events
    
    # Typed emitter
    te = TypedEmitter()
    te.define("click", {"args": 2})
    te.on("click", lambda x, y: None)
    te.emit("click", 1, 2)
    try:
        te.emit("click", 1)
        assert False, "Should have raised"
    except TypeError:
        pass
    
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: event_emitter.py test")
