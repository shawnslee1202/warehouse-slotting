import unittest
from collections import Counter
import numpy as np
import pandas as pd
from warehouse_slotting.model.layout import Layout,assign
from warehouse_slotting.model.routing import route,analytic_distance,mapping_from,Move,Visit
from warehouse_slotting.model.simulation import Batch,simulate
from warehouse_slotting.data.prepare import split_hash

class ModelTests(unittest.TestCase):
    def setUp(self):
        self.layout=Layout({'ambient':[0,1,2],'chilled':[3],'frozen':[4]},slots=5)
        self.mapping={i:('ambient',i//5,(i%5)+1) for i in range(15)}
        self.mapping.update({15:('chilled',3,2),16:('frozen',4,3)})
    def batch(self,lines,routing='s_shape'):
        return Batch(route(lines,self.mapping,self.layout,routing),1,len(lines),analytic_distance(lines,self.mapping,self.layout,routing))
    def test_hand_calculations(self):
        self.assertEqual(analytic_distance([0],self.mapping,self.layout),10)
        self.assertEqual(analytic_distance([0,5],self.mapping,self.layout),28)
        self.assertEqual(analytic_distance([0,5,10],self.mapping,self.layout),38)
        self.assertEqual(analytic_distance([0,5,10],self.mapping,self.layout,'largest_gap'),38)
    def test_route_distance_and_pick_conservation(self):
        rng=np.random.default_rng(41)
        for routing in ['s_shape','largest_gap']:
            for _ in range(200):
                lines=rng.integers(0,17,size=rng.integers(1,50)).tolist(); b=self.batch(lines,routing)
                walk=sum(o.distance if isinstance(o,Move) else o.distance(self.layout.pitch) for o in b.ops)
                self.assertAlmostEqual(walk,b.distance)
                self.assertEqual(sum(sum(o.picks.values()) for o in b.ops if isinstance(o,Visit)),len(lines))
                visits=[o.aisle for o in b.ops if isinstance(o,Visit)]
                if 4 in visits: self.assertTrue(all(a==4 for a in visits[visits.index(4):]))
    def test_one_picker_analytic_service(self):
        for routing in ['s_shape','largest_gap']:
            b=self.batch([0,0,2,7,12,15,16],routing)
            r,tours,_=simulate([b],self.layout,1,warmup=0,hours=.5,trace=True)
            self.assertEqual(r['blocking_share'],0)
            for t in tours: self.assertAlmostEqual(t['tour_seconds'],b.distance/1.2+b.lines*15+30)
    def test_blocking_and_passing_control(self):
        b=self.batch([0]*8+[1]*3)
        blocked=simulate([b],self.layout,4,warmup=0,hours=.5)
        passing=simulate([b],self.layout,4,warmup=0,hours=.5,passing=True)
        self.assertGreater(blocked['blocking_share'],0)
        self.assertEqual(passing['blocking_share'],0)
        self.assertGreater(passing['orders_completed'],blocked['orders_completed'])
    def test_mixed_directions_no_deadlock(self):
        batches=[self.batch([0,6]),self.batch([5,12]),self.batch([0,3])]
        r=simulate(batches,self.layout,12,warmup=0,hours=1)
        self.assertGreater(r['tours_completed'],20)
    def test_time_and_flow_conservation(self):
        r=simulate([self.batch([0,7])],self.layout,4,warmup=137,hours=.5,arrival_rate=100)
        self.assertAlmostEqual(sum(r[k] for k in ['travel_hours','pick_hours','blocking_hours','idle_hours','depot_hours']),2)
        self.assertEqual(r['wip_start']+r['arrivals_window']-r['orders_completed'],r['wip_end'])
    def test_split_stable_and_disjoint(self):
        ids=np.arange(100000); held=split_hash(ids)%5==0
        self.assertTrue(.19<held.mean()<.21); self.assertTrue(np.array_equal(split_hash(ids[:10]),split_hash(ids)[:10]))
    def test_slots_unique_zone_valid(self):
        frame=pd.DataFrame([dict(product_id=i,zone=z,train_lines=100-i) for i,(z,a,d) in self.mapping.items()])
        for policy in ['Random','ABC','Spread','Concentration']:
            result=assign(frame,self.layout,policy,concentration=.5 if policy=='Concentration' else None)
            self.assertFalse(result.duplicated(['aisle','depth','side']).any())
            for r in result.itertuples(): self.assertIn(r.aisle,self.layout.zone_aisles[r.zone])

if __name__=='__main__': unittest.main()
