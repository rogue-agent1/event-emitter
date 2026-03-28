#!/usr/bin/env python3
"""event_emitter - Event-driven programming pattern."""
import sys
from collections import defaultdict
class EventEmitter:
    def __init__(s):s._handlers=defaultdict(list);s._once=set()
    def on(s,event,handler):s._handlers[event].append(handler)
    def once(s,event,handler):s._handlers[event].append(handler);s._once.add((event,id(handler)))
    def emit(s,event,*args,**kwargs):
        for handler in list(s._handlers[event]):
            handler(*args,**kwargs)
            if(event,id(handler)) in s._once:s._handlers[event].remove(handler);s._once.discard((event,id(handler)))
    def off(s,event,handler=None):
        if handler:s._handlers[event]=[h for h in s._handlers[event] if h!=handler]
        else:del s._handlers[event]
    def listeners(s,event):return len(s._handlers[event])
class TypedEmitter(EventEmitter):
    def __init__(s,events=None):super().__init__();s._valid=set(events) if events else None
    def emit(s,event,*args,**kwargs):
        if s._valid and event not in s._valid:raise ValueError(f"Unknown event: {event}")
        super().emit(event,*args,**kwargs)
if __name__=="__main__":
    ee=EventEmitter();log=[]
    ee.on("data",lambda d:log.append(f"received: {d}"))
    ee.once("connect",lambda:log.append("connected!"))
    ee.emit("connect");ee.emit("connect")
    ee.emit("data","hello");ee.emit("data","world")
    for l in log:print(f"  {l}")
    print(f"  data listeners: {ee.listeners('data')}")
