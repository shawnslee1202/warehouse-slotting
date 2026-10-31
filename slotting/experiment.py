"""Reproducible experiment runner. Raw data are never required to inspect results."""
from pathlib import Path
import argparse,json,pickle,time
import numpy as np
import pandas as pd
from scipy.stats import t
from .prepare import scope_data
from .layout import make_layout,assign
from .routing import route,analytic_distance,mapping_from,Move,Visit
from .simulation import Batch,simulate

PICKERS=[1,2,4,6,8,12,16,20]
POLICIES=['Random','ABC','Affinity','Spread']

def interval(v):
    v=np.asarray(v,dtype=float); v=v[np.isfinite(v)]
    mean=float(v.mean()); h=float(t.ppf(.975,len(v)-1)*v.std(ddof=1)/np.sqrt(len(v))) if len(v)>1 else 0
    return mean,mean-h,mean+h

def build(processed,cache,results):
    cache,results=Path(cache),Path(results); cache.mkdir(exist_ok=True,parents=True); results.mkdir(exist_ok=True,parents=True)
    import shutil
    for filename in ['data_summary.json','sku_velocity.csv','order_time_profile.csv']:
        source=Path(processed)/filename
        if source.exists(): shutil.copy2(source,results/filename)
    summaries=[]; analytic=[]; paired=[]; verify=[]
    for scope in ['compact800','coverage90']:
        print('Building',scope,flush=True); sku,aff,baskets,summary=scope_data(processed,scope); layout=make_layout(sku,scope)
        from scipy.sparse import triu
        co=triu(aff,k=1).tocoo(); ix=np.argsort(co.data)[-5000:][::-1]; ids=sku.product_id.to_numpy()
        pd.DataFrame(dict(product_id_1=ids[co.row[ix]],product_id_2=ids[co.col[ix]],sampled_training_orders_together=co.data[ix])).to_csv(results/f'top_affinities_{scope}.csv',index=False)
        summary.update(aisles=layout.aisles,slots_per_side=layout.slots,capacity=layout.aisles*layout.slots*2,aisle_length_m=layout.length)
        summaries.append(summary); assignments={}; distances={}
        workload=[]
        for pol in POLICIES+['A50','A100']:
            frame=assign(sku,layout,pol,affinity=aff,concentration={'A50':.5,'A100':1.0}.get(pol))
            frame.to_csv(results/f'slotting_{scope}_{pol}.csv',index=False);
            work=frame.merge(sku[['product_id','train_lines']],on='product_id').groupby(['zone','aisle']).train_lines.sum().reset_index(); work['policy']=pol; work['training_work_share']=work.train_lines/work.train_lines.sum(); workload.append(work)
            assignments[pol]=mapping_from(frame)
            if pol not in POLICIES: continue
            for routing in ['s_shape','largest_gap']:
                d=np.array([analytic_distance(b,assignments[pol],layout,routing) for b in baskets]); distances[pol,routing]=d
                mean,lo,hi=interval(d); analytic.append(dict(scope=scope,policy=pol,routing=routing,n=len(d),meters_per_order=mean,ci_low=lo,ci_high=hi))
                # Independent path sum plus actual one-picker time, on 20 varied held-out orders.
                for oid,lines in list(baskets.items())[:20]:
                    ops=route(lines,assignments[pol],layout,routing); expected=analytic_distance(lines,assignments[pol],layout,routing)
                    path=sum(o.distance if isinstance(o,Move) else o.distance(layout.pitch) for o in ops)
                    batch=Batch(ops,1,len(lines),expected)
                    result,tours,_=simulate([batch],layout,1,warmup=0,hours=(expected/1.2+len(lines)*15+31)/3600,trace=True)
                    elapsed=tours[0]['tour_seconds']; theory=expected/1.2+15*len(lines)+30
                    verify.append(dict(scope=scope,policy=pol,routing=routing,order_id=oid,analytic_m=expected,path_m=path,simulation_seconds=elapsed,theory_seconds=theory,relative_error=(elapsed-theory)/theory,blocking_seconds=tours[0]['blocking_seconds']))
        for routing in ['s_shape','largest_gap']:
            for pol in POLICIES:
                base=distances['ABC',routing]; d=distances[pol,routing]; mean,lo,hi=interval(d-base)
                paired.append(dict(scope=scope,routing=routing,policy=pol,meters_minus_ABC=mean,ci_low=lo,ci_high=hi,percent_saving_vs_ABC=100*(1-d.mean()/base.mean()),percent_saving_vs_random=100*(1-d.mean()/distances['Random',routing].mean())))
        pd.concat(workload).to_csv(results/f'aisle_workload_{scope}.csv',index=False)
        # Fixed demand scenario based on 70% of eight-picker, uncongested ABC capacity.
        rng=np.random.default_rng(700); bb=baskets.tolist(); sample=rng.integers(0,len(bb),size=(1000,3))
        seconds=np.mean([analytic_distance(sum([bb[i] for i in row],[]),assignments['ABC'],layout)/1.2+15*sum(len(bb[i]) for i in row)+30 for row in sample])
        summary['demand_orders_hour']=round(.70*8*3*3600/seconds,1)
        bundle=dict(layout=layout,assignments=assignments,baskets=bb,summary=summary)
        with (cache/f'{scope}.pkl').open('wb') as f: pickle.dump(bundle,f)
        (results/f'layout_{scope}.json').write_text(json.dumps(layout.to_dict(),indent=2))
        print(summary,flush=True)
    pd.DataFrame(summaries).to_csv(results/'scope_summary.csv',index=False)
    pd.DataFrame(analytic).to_csv(results/'single_picker_travel.csv',index=False)
    pd.DataFrame(paired).to_csv(results/'paired_travel_comparisons.csv',index=False)
    pd.DataFrame(verify).to_csv(results/'verification.csv',index=False)

def design():
    scenarios=[]
    def add(scope,pol,k=3,routing='s_shape',passing=False,warmup=3600,speed=1.2,pick_seconds=15,mode='capacity',pickers=PICKERS,family='baseline'):
        for p in pickers: scenarios.append(dict(scope=scope,policy=pol,k=k,routing=routing,passing=passing,warmup=warmup,speed=speed,pick_seconds=pick_seconds,mode=mode,pickers=p,family=family))
    for scope in ['compact800','coverage90']:
        for pol in POLICIES:
            add(scope,pol)
            add(scope,pol,mode='demand',family='demand')
        for pol in ['ABC','Spread']:
            for k in [1,5]: add(scope,pol,k=k,pickers=[1,8,20],family='batching')
            add(scope,pol,routing='largest_gap',pickers=[1,8,20],family='routing')
            add(scope,pol,passing=True,pickers=[1,8,12,20],family='passing')
    for pol in ['A50','A100']: add('compact800',pol,family='concentration')
    for pol in ['ABC','Spread']:
        add('compact800',pol,warmup=7200,pickers=[8,20],family='warmup')
        for sec in [10,20]: add('compact800',pol,pick_seconds=sec,pickers=[8,20],family='pick_time')
        for speed in [1.0,1.3]: add('compact800',pol,speed=speed,pickers=[8,20],family='walk_speed')
    return scenarios

def batches_for(bundle,policy,k,routing,rep,count=4096):
    rng=np.random.default_rng(10000+rep); baskets=bundle['baskets']; layout=bundle['layout']; mapping=bundle['assignments'][policy]
    samples=rng.integers(0,len(baskets),size=(count,k)); batches=[]
    for row in samples:
        lines=sum([baskets[i] for i in row],[]); distance=analytic_distance(lines,mapping,layout,routing)
        batches.append(Batch(route(lines,mapping,layout,routing),k,len(lines),distance))
    return batches

def run_group(args):
    """One process per scope/policy/routing/batch/rep group; shared draws across staffing."""
    cache,group,rep=args
    scope,policy,k,routing=group[0]['scope'],group[0]['policy'],group[0]['k'],group[0]['routing']
    with (Path(cache)/f'{scope}.pkl').open('rb') as f: bundle=pickle.load(f)
    batches=batches_for(bundle,policy,k,routing,rep)
    results=[]
    for scenario in group:
        demand=bundle['summary']['demand_orders_hour'] if scenario['mode']=='demand' else None
        r=simulate(batches,bundle['layout'],scenario['pickers'],seed=20000+rep,arrival_rate=demand,passing=scenario['passing'],warmup=scenario['warmup'],speed=scenario['speed'],pick_seconds=scenario['pick_seconds'])
        r.update(scenario); r.update(rep=rep,arrival_rate=demand,seed=20000+rep); results.append(r)
    return results

def run(cache,results,workers=4,reps=10):
    from concurrent.futures import ProcessPoolExecutor,as_completed
    results=Path(results); scenarios=design(); pd.DataFrame(scenarios).to_csv(results/'experiment_design.csv',index=False)
    groupmap={}
    for s in scenarios: groupmap.setdefault((s['scope'],s['policy'],s['k'],s['routing']),[]).append(s)
    jobs=[(str(Path(cache).resolve()),g,r) for g in groupmap.values() for r in range(reps)]
    done=set(); path=results/'replications.csv'
    if path.exists():
        old=pd.read_csv(path)
        for key,g in old.groupby(['scope','policy','k','routing','rep']):
            if len(g)==len(groupmap[key[:4]]): done.add(key)
    jobs=[j for j in jobs if (j[1][0]['scope'],j[1][0]['policy'],j[1][0]['k'],j[1][0]['routing'],j[2]) not in done]
    print('Experiment cells',len(scenarios),'replications',reps,'remaining groups',len(jobs),flush=True)
    start=time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(run_group,j) for j in jobs]
        for n,f in enumerate(as_completed(futures),1):
            df=pd.DataFrame(f.result()); df.to_csv(path,mode='a',header=not path.exists(),index=False)
            print(f'Finished {n}/{len(jobs)} groups; {time.time()-start:.0f}s',flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser(); a.add_argument('stage',choices=['build','run']); a.add_argument('--processed',default='../../work/processed'); a.add_argument('--cache',default='../../work/cache'); a.add_argument('--results',default='results'); a.add_argument('--workers',type=int,default=4); a.add_argument('--reps',type=int,default=10)
    x=a.parse_args()
    if x.stage=='build': build(x.processed,x.cache,x.results)
    else: run(x.cache,x.results,x.workers,x.reps)

