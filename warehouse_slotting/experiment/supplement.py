"""Predeclared follow-up: explain blocking, test density scaling, evaluate k=5 staffing."""
import argparse,pickle
from pathlib import Path
import pandas as pd
from concurrent.futures import ProcessPoolExecutor,as_completed
from warehouse_slotting.experiment.run import run_group,PICKERS

def jobs(cache):
    for scope in ['compact800','coverage90']:
        for pol in ['ABC','Spread']:
            for k in [3,5]:
                group=[]
                def add(p,mode,family):
                    group.append(dict(scope=scope,policy=pol,k=k,routing='s_shape',passing=False,warmup=3600,speed=1.2,pick_seconds=15,mode=mode,pickers=p,family=family))
                if k==3:
                    for p in [8,20]: add(p,'capacity','blocking_components')
                    if scope=='coverage90':
                        for p in [23,46,69,92,138,184,230]: add(p,'capacity','density_extension')
                else:
                    for p in PICKERS:
                        add(p,'demand','demand_k5')
                        if p not in [1,8,20]: add(p,'capacity','batching_grid')
                for rep in range(10): yield str(Path(cache).resolve()),group,rep

def run(cache,results):
    results=Path(results); path=results/'supplemental_replications.csv'
    if path.exists(): raise FileExistsError('Supplement already exists; use a new results directory to rerun')
    todo=list(jobs(cache)); pd.DataFrame([s for _,g,r in todo if r==0 for s in g]).to_csv(results/'supplemental_design.csv',index=False)
    with ProcessPoolExecutor(max_workers=4) as pool:
        fs=[pool.submit(run_group,j) for j in todo]
        for n,f in enumerate(as_completed(fs),1):
            pd.DataFrame(f.result()).to_csv(path,mode='a',header=not path.exists(),index=False)
            print(f'Supplement {n}/{len(fs)}',flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser(); a.add_argument('--cache',required=True); a.add_argument('--results',required=True); x=a.parse_args(); run(x.cache,x.results)
