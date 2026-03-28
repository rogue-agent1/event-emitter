#!/usr/bin/env python3
"""Event emitter / pub-sub system."""
import sys, json
from collections import defaultdict

class EventEmitter:
    def __init__(self):
        self.listeners = defaultdict(list)
        self.once_listeners = set()
    def on(self, event, fn):
        self.listeners[event].append(fn)
    def once(self, event, fn):
        self.listeners[event].append(fn)
        self.once_listeners.add((event, id(fn)))
    def emit(self, event, *args, **kwargs):
        remove = []
        for fn in self.listeners[event]:
            fn(*args, **kwargs)
            if (event, id(fn)) in self.once_listeners:
                remove.append(fn)
                self.once_listeners.discard((event, id(fn)))
        for fn in remove: self.listeners[event].remove(fn)
    def off(self, event, fn=None):
        if fn: self.listeners[event].remove(fn)
        else: del self.listeners[event]
    def count(self, event=None):
        if event: return len(self.listeners[event])
        return sum(len(v) for v in self.listeners.values())

if __name__ == '__main__':
    ee = EventEmitter()
    log = []
    ee.on('data', lambda x: log.append(f'listener1: {x}'))
    ee.on('data', lambda x: log.append(f'listener2: {x}'))
    ee.once('ready', lambda: log.append('ready! (once)'))
    ee.emit('ready'); ee.emit('ready')
    ee.emit('data', 'hello'); ee.emit('data', 'world')
    print("Event log:")
    for l in log: print(f"  {l}")
    print(f"\nActive listeners: {ee.count()}")
