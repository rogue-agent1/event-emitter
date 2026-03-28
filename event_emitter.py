#!/usr/bin/env python3
"""Event emitter / pub-sub system."""
import sys
from collections import defaultdict
class EventEmitter:
    def __init__(self): self._handlers=defaultdict(list);self._once=set()
    def on(self,event,handler): self._handlers[event].append(handler);return self
    def once(self,event,handler): self._handlers[event].append(handler);self._once.add((event,id(handler)));return self
    def off(self,event,handler=None):
        if handler: self._handlers[event]=[h for h in self._handlers[event] if h!=handler]
        else: del self._handlers[event]
    def emit(self,event,*args,**kwargs):
        for h in list(self._handlers[event]):
            h(*args,**kwargs)
            if (event,id(h)) in self._once:
                self._once.discard((event,id(h)))
                self._handlers[event].remove(h)
        # Wildcard
        for h in list(self._handlers['*']): h(event,*args,**kwargs)
    def listeners(self,event): return list(self._handlers[event])
def main():
    ee=EventEmitter()
    ee.on('data',lambda x:print(f"  Handler A: {x}"))
    ee.on('data',lambda x:print(f"  Handler B: {x}"))
    ee.once('connect',lambda:print("  Connected! (once)"))
    ee.on('*',lambda evt,*a:print(f"  [wildcard] event={evt}"))
    print("Emit 'connect':"); ee.emit('connect')
    print("Emit 'connect' again:"); ee.emit('connect')
    print("Emit 'data':"); ee.emit('data',42)
    print(f"\nListeners for 'data': {len(ee.listeners('data'))}")
if __name__=="__main__": main()
