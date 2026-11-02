"""SimPy cell-occupancy model, explicit traffic control and time accounting."""
from collections import deque,Counter
from dataclasses import dataclass
import numpy as np
import simpy
from warehouse_slotting.model.routing import Move,Visit

class DirectionGate:
    """FIFO group admission. Same-direction traversals share an aisle.
    Returning visits are exclusive, preventing head-on gridlock at U-turns.
    Once an incompatible request queues, later traffic cannot bypass it.
    """
    def __init__(self,env): self.env=env; self.active=0; self.mode=None; self.queue=deque()
    def request(self,mode):
        event=self.env.event(); self.queue.append((mode,event)); self._admit(); return event
    def _admit(self):
        while self.queue:
            mode,event=self.queue[0]
            if self.active and (mode!=self.mode or mode=='return'): break
            self.queue.popleft(); self.mode=mode; self.active+=1; event.succeed()
            if mode=='return': break
    def release(self):
        self.active-=1
        if not self.active: self.mode=None
        self._admit()

@dataclass
class Batch:
    ops: list
    orders: int
    lines: int
    distance: float

class Ledger:
    def __init__(self,env,warm,end): self.env=env; self.warm=warm; self.end=end; self.since=env.now; self.state='idle'; self.total=Counter()
    def switch(self,new):
        self.total[self.state]+=max(0,min(self.env.now,self.end)-max(self.since,self.warm)); self.since=self.env.now; self.state=new


def simulate(batches,layout,pickers,seed=0,arrival_rate=None,passing=False,warmup=3600,hours=8,speed=1.2,pick_seconds=15,depot_seconds=30,trace=False):
    if pickers<1 or not batches: raise ValueError('Need at least one picker and one batch')
    env=simpy.Environment(); end=warmup+hours*3600; rng=np.random.default_rng(seed)
    cells=[[simpy.Resource(env,capacity=1) for _ in range(layout.slots+2)] for _ in range(layout.aisles)]
    gates=[DirectionGate(env) for _ in range(layout.aisles)]
    ledgers=[]; completed=[]; completed_window=0; arrived=0; initial_wip=0; batch_counter=0; tours=[]
    store=simpy.Store(env); eventlog=[]
    def arrivals():
        nonlocal arrived
        buffer=0; first=None
        while True:
            yield env.timeout(rng.exponential(3600/arrival_rate)); arrived+=1
            if not buffer: first=env.now
            buffer+=1
            if buffer==batches[0].orders:
                yield store.put((first,env.now)); buffer=0
    def start_measurement():
        nonlocal initial_wip
        yield env.timeout(warmup); initial_wip=arrived-sum(x[1] for x in completed)
    def worker(wid):
        nonlocal batch_counter,completed_window
        ledger=Ledger(env,warmup,end); ledgers.append(ledger)
        while True:
            ledger.switch('idle')
            if arrival_rate is not None:
                first,ready=yield store.get()
            else: first=ready=env.now
            batch=batches[batch_counter%len(batches)]; batch_counter+=1
            started=env.now; travel=pick=blocking=0.0
            for op in batch.ops:
                if isinstance(op,Move):
                    t=op.distance/speed; ledger.switch('travel'); yield env.timeout(t); travel+=t
                    continue
                gate=gates[op.aisle]
                if not passing:
                    t0=env.now; ledger.switch('gate_blocking')
                    yield gate.request('return' if op.returning else ('up' if op.entry==0 else 'down'))
                    blocking+=env.now-t0
                current=None; request=None; picked=set()
                for cell in op.cells():
                    next_resource=cells[op.aisle][cell] if 1<=cell<=layout.slots else None
                    next_request=None
                    if not passing and next_resource is not None:
                        t0=env.now; ledger.switch('cell_blocking'); next_request=next_resource.request(); yield next_request; blocking+=env.now-t0
                    if current is not None: current.release(request)
                    current=next_resource if not passing else None; request=next_request
                    t=layout.pitch/speed; ledger.switch('travel'); yield env.timeout(t); travel+=t
                    if trace: eventlog.append((env.now,wid,op.aisle,cell))
                    if cell in op.picks and cell not in picked:
                        t=op.picks[cell]*pick_seconds; ledger.switch('pick'); yield env.timeout(t); pick+=t; picked.add(cell)
                if current is not None: current.release(request)
                if not passing: gate.release()
            ledger.switch('depot'); yield env.timeout(depot_seconds)
            assert abs(travel-batch.distance/speed)<1e-6
            assert abs(pick-batch.lines*pick_seconds)<1e-6
            assert abs(env.now-started-travel-pick-blocking-depot_seconds)<1e-5
            completed.append((env.now,batch.orders))
            if env.now>=warmup:
                completed_window+=batch.orders
                tours.append(dict(tour_seconds=env.now-started,travel_seconds=travel,pick_seconds=pick,blocking_seconds=blocking,orders=batch.orders,lines=batch.lines,distance=batch.distance,queue_seconds=started-ready,oldest_order_seconds=env.now-first))
    if arrival_rate is not None: env.process(arrivals()); env.process(start_measurement())
    for i in range(pickers): env.process(worker(i))
    env.run(until=end)
    total=Counter()
    for l in ledgers: l.switch('idle'); total.update(l.total)
    horizon=hours*3600; available=pickers*horizon; assert abs(sum(total.values())-available)<.001
    total['blocking']=total['gate_blocking']+total['cell_blocking']
    active=available-total['idle']; lines=sum(t['lines'] for t in tours)
    result=dict(orders_per_hour=completed_window/hours,lines_per_hour=lines/hours,orders_completed=completed_window,tours_completed=len(tours),
        mean_tour_seconds=float(np.mean([t['tour_seconds'] for t in tours])) if tours else float('nan'),
        mean_queue_seconds=float(np.mean([t['queue_seconds'] for t in tours])) if tours else float('nan'),
        mean_oldest_order_seconds=float(np.mean([t['oldest_order_seconds'] for t in tours])) if tours else float('nan'),
        blocking_share=total['blocking']/active if active else 0,utilization=active/available,productive_utilization=(total['travel']+total['pick']+total['depot'])/available,
        gate_blocking_hours=total['gate_blocking']/3600,cell_blocking_hours=total['cell_blocking']/3600,travel_hours=total['travel']/3600,pick_hours=total['pick']/3600,blocking_hours=total['blocking']/3600,idle_hours=total['idle']/3600,depot_hours=total['depot']/3600,
        labor_hours_per_1000=1000*pickers*hours/completed_window if completed_window else float('inf'),
        batches_started=batch_counter,stream_recycled=batch_counter>len(batches),arrivals_total=arrived,wip_start=initial_wip,wip_end=arrived-sum(x[1] for x in completed) if arrival_rate is not None else 0,
        arrivals_window=arrived-(initial_wip+sum(x[1] for x in completed if x[0]<warmup)) if arrival_rate is not None else 0)
    if arrival_rate is not None:
        assert result['wip_start']+result['arrivals_window']-completed_window==result['wip_end']
    if trace: return result,tours,eventlog
    return result
