"""S-shape and largest-gap tours; independent closed-form distance check."""
from collections import Counter,defaultdict
from dataclasses import dataclass
from warehouse_slotting.model.layout import ZONES

@dataclass(frozen=True)
class Move:
    distance: float
@dataclass
class Visit:
    aisle: int
    entry: int
    turn: int
    exit: int
    picks: dict
    def cells(self):
        step=1 if self.turn>self.entry else -1
        path=list(range(self.entry+step,self.turn+step,step))
        if self.exit!=self.turn:
            step=1 if self.exit>self.turn else -1
            path+=list(range(self.turn+step,self.exit+step,step))
        return path
    @property
    def returning(self): return self.entry==self.exit
    def distance(self,pitch): return (abs(self.turn-self.entry)+abs(self.exit-self.turn))*pitch

def group_lines(lines,mapping):
    groups=defaultdict(lambda:defaultdict(Counter))
    for pid in lines:
        z,a,d=mapping[pid]; groups[z][a][d]+=1
    return groups

def largest_split(picks,end):
    points=[0]+sorted(picks)+[end]
    i=max(range(len(points)-1),key=lambda j:points[j+1]-points[j])
    return points[i],points[i+1]

def route(lines,mapping,layout,routing='s_shape'):
    groups=group_lines(lines,mapping); ops=[]; x=0; end=layout.slots+1
    def move(nx):
        nonlocal x
        if nx!=x: ops.append(Move(abs(nx-x)))
        x=nx
    for z in ZONES:
        g=groups.get(z,{})
        if not g: continue
        aa=sorted(g); anchor=layout.x(aa[0]); move(anchor)
        if routing=='s_shape':
            rear=False
            for j,a in enumerate(aa):
                move(layout.x(a))
                if j==len(aa)-1 and not rear:
                    ops.append(Visit(a,0,max(g[a]),0,dict(g[a])))
                else:
                    entry=end if rear else 0; dest=0 if rear else end
                    ops.append(Visit(a,entry,dest,dest,dict(g[a]))); rear=not rear
            assert not rear
        elif routing=='largest_gap':
            if len(aa)==1: ops.append(Visit(aa[0],0,max(g[aa[0]]),0,dict(g[aa[0]])))
            else:
                ops.append(Visit(aa[0],0,end,end,dict(g[aa[0]])))
                for a in aa[1:-1]:
                    low,high=largest_split(g[a],end)
                    if high<end:
                        move(layout.x(a)); ops.append(Visit(a,end,high,end,{d:n for d,n in g[a].items() if d>=high}))
                move(layout.x(aa[-1])); ops.append(Visit(aa[-1],end,0,0,dict(g[aa[-1]])))
                for a in reversed(aa[1:-1]):
                    low,high=largest_split(g[a],end)
                    if low>0:
                        move(layout.x(a)); ops.append(Visit(a,0,low,0,{d:n for d,n in g[a].items() if d<=low}))
        else: raise ValueError(routing)
        move(anchor)
    move(0)
    assert sum(sum(op.picks.values()) for op in ops if isinstance(op,Visit))==len(lines)
    return ops

def analytic_distance(lines,mapping,layout,routing='s_shape'):
    groups=group_lines(lines,mapping); vertical=0; horizontal=0; furthest_anchor=0; end=layout.slots+1
    for g in groups.values():
        aa=sorted(g); n=len(aa); horizontal+=2*(layout.x(aa[-1])-layout.x(aa[0])); furthest_anchor=max(furthest_anchor,layout.x(aa[0]))
        if routing=='s_shape': vertical+=(n-(n%2))*end+(2*max(g[aa[-1]]) if n%2 else 0)
        elif n==1: vertical+=2*max(g[aa[0]])
        else:
            vertical+=2*end
            for a in aa[1:-1]:
                points=[0]+sorted(g[a])+[end]; gap=max(b-a for a,b in zip(points,points[1:])); vertical+=2*(end-gap)
    return horizontal+2*furthest_anchor+vertical*layout.pitch

def mapping_from(frame): return {int(r.product_id):(r.zone,int(r.aisle),int(r.depth)) for r in frame.itertuples()}
