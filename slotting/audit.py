"""Data integrity and result-completeness audit."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from .prepare import split_hash

def audit_raw(raw,out):
    raw,out=Path(raw),Path(out)
    import shutil
    if (raw/'manifest.json').exists(): shutil.copy2(raw/'manifest.json',out/'data_manifest.json')
    products=pd.read_csv(raw/'products.csv'); orders=pd.read_csv(raw/'orders.csv',usecols=['order_id','eval_set'])
    assert products.product_id.is_unique and orders.order_id.is_unique
    valid_order=np.zeros(int(orders.order_id.max())+1,dtype=bool); valid_order[orders.loc[orders.eval_set=='prior','order_id']]=True
    valid_product=np.zeros(int(products.product_id.max())+1,dtype=bool); valid_product[products.product_id]=True
    rows=0; distinct=0; last=-1; carry=pd.DataFrame(); train=held=0
    for chunk in pd.read_csv(raw/'order_products__prior.csv',dtype='int32',chunksize=2_000_000):
        assert not chunk.isna().any().any(); assert valid_order[chunk.order_id].all(); assert valid_product[chunk.product_id].all()
        o=chunk.order_id.to_numpy(); assert np.all(o[1:]>=o[:-1]) and o[0]>=last
        both=pd.concat([carry,chunk],ignore_index=True); assert not both.duplicated(['order_id','product_id']).any()
        distinct+=int(np.count_nonzero(o[1:]!=o[:-1]))+int(o[0]!=last); last=int(o[-1]); carry=chunk.loc[chunk.order_id==last]
        h=split_hash(o)%5==0; held+=int(h.sum()); train+=int((~h).sum()); rows+=len(chunk)
    report=dict(prior_lines=rows,prior_orders=distinct,product_catalog_rows=len(products),order_metadata_rows=len(orders),train_lines=train,holdout_lines=held,duplicate_order_products=0,missing_foreign_keys=0,missing_line_values=0,order_ids_sorted=True)
    assert rows==32434489 and distinct==3214874 and len(products)==49688
    (out/'data_integrity.json').write_text(json.dumps(report,indent=2)); print(report)

def audit_results(root):
    root=Path(root); r=root/'results'; main=pd.read_csv(r/'replications.csv'); extra=pd.read_csv(r/'supplemental_replications.csv'); verify=pd.read_csv(r/'verification.csv')
    from .analyze import KEYS
    allrows=pd.concat([main,extra],ignore_index=True)
    assert not allrows.duplicated(KEYS+['rep']).any()
    counts=allrows.groupby(KEYS).size(); assert (counts==10).all()
    assert not allrows.stream_recycled.any()
    assert np.isfinite(allrows.orders_per_hour).all() and (allrows.orders_per_hour>0).all()
    assert np.allclose(allrows[['travel_hours','pick_hours','blocking_hours','idle_hours','depot_hours']].sum(axis=1),allrows.pickers*8)
    d=allrows.loc[allrows['mode']=='demand']; assert ((d.wip_start+d.arrivals_window-d.orders_completed)==d.wip_end).all()
    assert (allrows.loc[allrows.pickers==1,'blocking_share'].abs()<1e-10).all()
    assert (allrows.loc[allrows.passing,'blocking_share'].abs()<1e-10).all()
    assert verify.relative_error.abs().max()<1e-10 and np.allclose(verify.analytic_m,verify.path_m)
    assert len(main)==2160 and len(extra)==740
    report=dict(main_replications=len(main),supplemental_replications=len(extra),experiment_cells=len(counts),replications_per_cell=10,one_picker_verification_cases=len(verify),max_relative_verification_error=float(verify.relative_error.abs().max()),stream_recycled=False,time_conservation=True,order_flow_conservation=True,single_picker_blocking_zero=True,passing_blocking_zero=True)
    (r/'validation.json').write_text(json.dumps(report,indent=2)); print(report)

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser(); a.add_argument('--root',default='.'); a.add_argument('--raw'); x=a.parse_args()
    if x.raw: audit_raw(x.raw,Path(x.root)/'results')
    else: audit_results(x.root)
