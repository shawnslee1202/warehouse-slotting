"""Training-only scoping, deterministic order split, and sparse affinities."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, save_npz

def split_hash(ids, salt=20261027):
    x=np.asarray(ids,dtype=np.uint64)+np.uint64(salt)
    x=(x^(x>>30))*np.uint64(0xbf58476d1ce4e5b9)
    x=(x^(x>>27))*np.uint64(0x94d049bb133111eb)
    return x^(x>>31)

def prepare(raw, out):
    raw,out=Path(raw),Path(out); out.mkdir(parents=True,exist_ok=True)
    products=pd.read_csv(raw/'products.csv').merge(pd.read_csv(raw/'departments.csv'),on='department_id')
    products['zone']=np.where(products.department.eq('frozen'),'frozen',np.where(products.department.isin(['dairy eggs','meat seafood','deli','produce']),'chilled','ambient'))
    orders=pd.read_csv(raw/'orders.csv',usecols=['order_id','eval_set','order_dow','order_hour_of_day'])
    prior=orders.loc[orders.eval_set.eq('prior')].copy(); prior['holdout']=(split_hash(prior.order_id)%5==0)
    maxid=int(orders.order_id.max()); hold=np.zeros(maxid+1,dtype=bool); hold[prior.order_id]=prior.holdout
    freq=np.zeros(int(products.product_id.max())+1,dtype=np.int64); lines=0
    for chunk in pd.read_csv(raw/'order_products__prior.csv',usecols=['order_id','product_id'],dtype='int32',chunksize=2_000_000):
        lines+=len(chunk); m=~hold[chunk.order_id.to_numpy()]; freq+=np.bincount(chunk.product_id.to_numpy()[m],minlength=len(freq))
    products['train_lines']=freq[products.product_id]
    ranked=products.sort_values(['train_lines','product_id'],ascending=[False,True]).copy()
    ranked['train_cumulative_share']=ranked.train_lines.cumsum()/ranked.train_lines.sum()
    n90=int(np.searchsorted(ranked.train_cumulative_share.to_numpy(),.90)+1)
    ranked.to_csv(out/'sku_velocity.csv',index=False); prior.to_csv(out/'order_split.csv',index=False)
    prior.groupby(['order_dow','order_hour_of_day']).size().rename('orders').reset_index().to_csv(out/'order_time_profile.csv',index=False)
    rng=np.random.default_rng(91827)
    tr_ids=rng.choice(prior.loc[~prior.holdout,'order_id'],min(120000,(~prior.holdout).sum()),replace=False)
    te_ids=rng.choice(prior.loc[prior.holdout,'order_id'],min(60000,prior.holdout.sum()),replace=False)
    want=np.zeros(maxid+1,dtype=bool); want[tr_ids]=True; want[te_ids]=True; chunks=[]
    for chunk in pd.read_csv(raw/'order_products__prior.csv',usecols=['order_id','product_id','add_to_cart_order'],dtype='int32',chunksize=2_000_000):
        chunks.append(chunk.loc[want[chunk.order_id.to_numpy()]])
    sampled=pd.concat(chunks,ignore_index=True); sampled.sort_values(['order_id','add_to_cart_order'],inplace=True)
    sampled['holdout']=hold[sampled.order_id.to_numpy()]; sampled.to_csv(out/'sampled_lines.csv.gz',index=False)
    meta=dict(total_prior_orders=len(prior),total_prior_lines=lines,train_orders=int((~prior.holdout).sum()),holdout_orders=int(prior.holdout.sum()),train_lines=int(freq.sum()),n90=n90,affinity_sample_orders=len(tr_ids),evaluation_sample_orders=len(te_ids),split_seed=20261027,sample_seed=91827)
    (out/'data_summary.json').write_text(json.dumps(meta,indent=2)); print(json.dumps(meta),flush=True)

def scope_data(processed, name='coverage90'):
    p=Path(processed); ranked=pd.read_csv(p/'sku_velocity.csv'); meta=json.loads((p/'data_summary.json').read_text())
    n=meta['n90'] if name=='coverage90' else 800
    sku=ranked.head(n).copy(); keep=set(sku.product_id); sample=pd.read_csv(p/'sampled_lines.csv.gz')
    sample['kept']=sample.product_id.isin(keep); complete=sample.groupby('order_id').kept.all(); ids=set(complete[complete].index)
    evaluation=sample.loc[sample.holdout]; eligible=evaluation.loc[evaluation.order_id.isin(ids)]
    baskets=eligible.groupby('order_id',sort=True).product_id.apply(list)
    training=sample.loc[(~sample.holdout)&sample.kept]; oi,_=pd.factorize(training.order_id,sort=True)
    mapping={int(v):i for i,v in enumerate(sku.product_id)}; pi=training.product_id.map(mapping).to_numpy()
    mat=csr_matrix((np.ones(len(pi),dtype=np.int32),(oi,pi)),shape=(oi.max()+1,n))
    affinity=(mat.T@mat).tocsr(); affinity.setdiag(0); affinity.eliminate_zeros(); save_npz(p/f'affinity_{name}.npz',affinity)
    summary=dict(scope=name,skus=n,train_line_coverage=float(sku.train_lines.sum()/meta['train_lines']),heldout_line_coverage=float(evaluation.kept.mean()),heldout_complete_order_fraction=float(len(baskets)/evaluation.order_id.nunique()),heldout_orders_before_exclusion=int(evaluation.order_id.nunique()),eligible_heldout_orders=len(baskets),mean_lines_all=float(len(evaluation)/evaluation.order_id.nunique()),mean_lines_eligible=float(len(eligible)/len(baskets)))
    return sku,affinity,baskets,summary

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser(); a.add_argument('--raw',required=True); a.add_argument('--out',required=True)
    x=a.parse_args(); prepare(x.raw,x.out)
