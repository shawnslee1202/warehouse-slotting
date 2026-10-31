"""Geometry, temperature constraints, velocity/affinity policies and concentration."""
from dataclasses import dataclass
from math import ceil
import numpy as np
import pandas as pd
ZONES=('ambient','chilled','frozen')

@dataclass
class Layout:
    zone_aisles: dict
    slots: int=40
    pitch: float=1.0
    spacing: float=4.0
    aisle_width: float=2.5
    @property
    def length(self): return (self.slots+1)*self.pitch
    @property
    def aisles(self): return sum(map(len,self.zone_aisles.values()))
    def x(self,a): return (a+1)*self.spacing
    def to_dict(self): return dict(zone_aisles=self.zone_aisles,slots=self.slots,pitch=self.pitch,spacing=self.spacing,aisle_width=self.aisle_width)

def make_layout(skus,scope):
    counts=skus.zone.value_counts().to_dict()
    if scope=='compact800':
        # Ten aisles, balanced by SKU counts; extend depth if zone rounding requires it.
        raw=np.array([counts.get(z,0) for z in ZONES],dtype=float); raw=10*raw/raw.sum()
        allocation=np.maximum(1,np.floor(raw).astype(int))
        while allocation.sum()<10: allocation[np.argmax(raw-allocation)]+=1
        while allocation.sum()>10:
            eligible=np.where(allocation>1,allocation-raw,-np.inf); allocation[np.argmax(eligible)]-=1
        slots=max(40,max(ceil(counts.get(z,0)/(2*a)) for z,a in zip(ZONES,allocation)))
    else:
        allocation=[max(1,ceil(counts.get(z,0)/80)) for z in ZONES]; slots=40
    start=0; zones={}
    for z,n in zip(ZONES,allocation): zones[z]=list(range(start,start+int(n))); start+=int(n)
    return Layout(zones,slots)

def assign(skus,layout,policy,affinity=None,seed=301,concentration=None):
    """ABC fills nearer aisles; spread balances fast movers across aisle fronts.
    concentration is fraction of each zone's aisles available to A-items (80% of zone lines),
    with a capacity floor. Fixed random assignment is conditional on the seed.
    """
    rng=np.random.default_rng(seed); indices={int(pid):i for i,pid in enumerate(skus.product_id)}
    records=[]; pid_array=list(map(int,skus.product_id))
    for zone in ZONES:
        frame=skus.loc[skus.zone.eq(zone)].sort_values(['train_lines','product_id'],ascending=[False,True])
        ids=list(map(int,frame.product_id)); aisles=layout.zone_aisles[zone]
        slots=[(a,d,s) for a in aisles for d in range(1,layout.slots+1) for s in (0,1)]
        if policy=='Random': rng.shuffle(slots)
        elif policy=='Spread': slots.sort(key=lambda t:(t[1],t[2],t[0]))
        elif policy=='Affinity':
            # Greedy strongest available neighbor placed beside current seed.
            remaining=set(ids); chain=[]
            for seed_pid in ids:
                if seed_pid not in remaining: continue
                current=seed_pid
                while current is not None:
                    chain.append(current); remaining.remove(current)
                    row=affinity.getrow(indices[current]); candidates=[(int(v),pid_array[j]) for j,v in zip(row.indices,row.data) if pid_array[j] in remaining]
                    current=max(candidates,key=lambda p:(p[0],-indices[p[1]]))[1] if candidates else None
            ids=chain
        if concentration is not None:
            cumulative=frame.train_lines.cumsum().to_numpy(); na=int(np.searchsorted(cumulative,.8*cumulative[-1])+1)
            m=max(ceil(na/(2*layout.slots)),ceil(concentration*len(aisles))); m=min(m,len(aisles))
            front=[s for s in slots if s[0] in aisles[:m]]; front.sort(key=lambda t:(t[1],t[2],t[0]))
            chosen=front[:na]; used=set(chosen); slots=chosen+sorted([s for s in slots if s not in used],key=lambda t:(t[1],t[2],t[0]))
        for pid,(a,d,s) in zip(ids,slots): records.append(dict(product_id=pid,zone=zone,aisle=a,depth=d,side=s,policy=policy))
    result=pd.DataFrame(records)
    assert len(result)==len(skus) and not result.duplicated(['aisle','depth','side']).any()
    return result
