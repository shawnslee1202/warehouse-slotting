import unittest
import numpy as np
from slotting.layout import Layout
from slotting.routing import route,analytic_distance
from slotting.simulation import Batch,simulate
from slotting.simulation_reference import simulate as reference

class ExactBackendTests(unittest.TestCase):
    def test_cell_event_equivalence(self):
        layout=Layout({'ambient':[0,1,2],'chilled':[3],'frozen':[4]},slots=6)
        mapping={i:('ambient' if i//6<3 else ('chilled' if i//6==3 else 'frozen'),i//6,i%6+1) for i in range(30)}
        rng=np.random.default_rng(72)
        for routing in ['s_shape','largest_gap']:
            batches=[]
            for _ in range(30):
                lines=rng.integers(0,30,17).tolist()
                batches.append(Batch(route(lines,mapping,layout,routing),3,len(lines),analytic_distance(lines,mapping,layout,routing)))
            for p in [1,4,12]:
                for passing in [False,True]:
                    for rate in [None,60]:
                        args=dict(pickers=p,seed=3,passing=passing,arrival_rate=rate,warmup=177,hours=.8)
                        a=simulate(batches,layout,**args); b=reference(batches,layout,**args)
                        for key in a:
                            self.assertAlmostEqual(a[key],b[key],places=7,msg=f'{routing} {p} {passing} {rate} {key}')
