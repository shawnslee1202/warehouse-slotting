"""Aggregate independent replications, paired comparisons, economics, and figures."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from warehouse_slotting.experiment.run import interval,POLICIES
KEYS=['scope','policy','k','routing','passing','warmup','speed','pick_seconds','mode','pickers','family']
METRICS=['orders_per_hour','lines_per_hour','mean_tour_seconds','mean_queue_seconds','mean_oldest_order_seconds','blocking_share','utilization','productive_utilization','labor_hours_per_1000','travel_hours','pick_hours','blocking_hours','idle_hours','wip_start','wip_end']
COLORS={'ABC':'#176B70','Spread':'#D16B38','Affinity':'#7961A5','Random':'#9AADB8','A50':'#418CB7','A100':'#CEAE3C'}
NAMES={'compact800':'10-aisle compact scope (800 SKUs)','coverage90':'115-aisle 90% line-coverage scope (9,149 SKUs)'}

def analyze(root):
    root=Path(root); results=root/'results'; figs=root/'figures'; figs.mkdir(exist_ok=True)
    raw=pd.read_csv(results/'replications.csv'); summaries=[]
    if (results/'supplemental_replications.csv').exists(): raw=pd.concat([raw,pd.read_csv(results/'supplemental_replications.csv')],ignore_index=True)
    if raw.duplicated(KEYS+['rep']).any(): raise ValueError('Duplicate replications')
    for key,g in raw.groupby(KEYS,dropna=False):
        row=dict(zip(KEYS,key)); row['replications']=len(g)
        for metric in METRICS:
            m,l,h=interval(g[metric]); row[metric]=m; row[metric+'_low']=l; row[metric+'_high']=h
        summaries.append(row)
    summary=pd.DataFrame(summaries); summary.to_csv(results/'summary.csv',index=False)
    paired=[]
    for scope in ['compact800','coverage90']:
        for family in ['baseline','demand','passing']:
            sub=raw.loc[(raw.scope==scope)&(raw.family==family)]
            for p,g in sub.groupby('pickers'):
                pivot=g.pivot(index='rep',columns='policy',values='orders_per_hour')
                if not {'ABC','Spread'}.issubset(pivot.columns): continue
                d=pivot.Spread-pivot.ABC; m,l,h=interval(d); se=d.std(ddof=1)/np.sqrt(len(d))
                # Eight staffing comparisons per layout: simultaneous Bonferroni intervals.
                multi=t.ppf(1-.05/(2*8),len(d)-1)*se
                paired.append(dict(scope=scope,family=family,pickers=p,spread_minus_abc=m,ci_low=l,ci_high=h,simultaneous_low=m-multi,simultaneous_high=m+multi))
    paired=pd.DataFrame(paired); paired.to_csv(results/'paired_throughput.csv',index=False)
    crossover=[]
    for scope in ['compact800','coverage90']:
        g=paired.loc[(paired.scope==scope)&(paired.family=='baseline')].sort_values('pickers')
        mean_first=None; robust_first=None; interpolated=None
        for i in range(1,len(g)):
            a,b=g.iloc[i-1],g.iloc[i]
            if a.spread_minus_abc<=0<b.spread_minus_abc and mean_first is None:
                mean_first=int(b.pickers); interpolated=float(a.pickers+(b.pickers-a.pickers)*(-a.spread_minus_abc)/(b.spread_minus_abc-a.spread_minus_abc))
        for _,r in g.iterrows():
            if r.simultaneous_low>0 and (g.loc[g.pickers>=r.pickers,'simultaneous_low']>0).all(): robust_first=int(r.pickers); break
        crossover.append(dict(scope=scope,first_tested_mean_reversal=mean_first,linear_interpolation_descriptive_only=interpolated,first_sustained_simultaneous_advantage=robust_first))
    (results/'crossovers.json').write_text(json.dumps(crossover,indent=2))
    scopes=pd.read_csv(results/'scope_summary.csv'); economics=[]
    for scope in scopes.scope:
        demand=float(scopes.loc[scopes.scope==scope,'demand_orders_hour'].iloc[0])
        for factor in [.5,1,1.5,2]:
            rate=demand*factor
            for pol in POLICIES:
                cap=summary.loc[(summary.scope==scope)&(summary.policy==pol)&(summary.family=='baseline')].sort_values('pickers')
                ok=cap.loc[cap.orders_per_hour_low>=rate/.85]
                if len(ok):
                    row=ok.iloc[0]; p=int(row.pickers); hours=p*1000/rate
                    economics.append(dict(scope=scope,demand_multiplier=factor,orders_hour=rate,policy=pol,recommended_pickers=p,capacity_low=row.orders_per_hour_low,reserve_target=.15,labor_hours_1000=hours,illustrative_dollars_1000=25*hours,demand_simulated=factor==1))
                else: economics.append(dict(scope=scope,demand_multiplier=factor,orders_hour=rate,policy=pol,recommended_pickers=np.nan,capacity_low=np.nan,reserve_target=.15,labor_hours_1000=np.nan,illustrative_dollars_1000=np.nan,demand_simulated=False))
    pd.DataFrame(economics).to_csv(results/'staffing_economics.csv',index=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.titleweight':'bold','savefig.dpi':180})
    for scope in scopes.scope:
        base=summary.loc[(summary.scope==scope)&(summary.family=='baseline')]
        for metric,ylabel,name in [('orders_per_hour','Completed orders / hour','throughput'),('blocking_share','Blocking / active picker time','blocking')]:
            fig,ax=plt.subplots(figsize=(9.5,5.2));
            for pol in POLICIES:
                g=base.loc[base.policy==pol].sort_values('pickers'); ax.plot(g.pickers,g[metric],'-o',label=pol,color=COLORS[pol],lw=2,ms=4)
                ax.fill_between(g.pickers,g[metric+'_low'],g[metric+'_high'],color=COLORS[pol],alpha=.13)
            ax.set(xlabel='Pickers on shift',ylabel=ylabel,title=NAMES[scope]+'\nCapacity experiment | 3 orders/tour | S-shape')
            ax.set_xticks([1,2,4,6,8,12,16,20]); ax.grid(axis='y',alpha=.2); ax.legend(ncol=4,frameon=False,loc='upper left')
            if metric=='blocking_share': ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1))
            else:
                c=next(c for c in crossover if c['scope']==scope)
                if c['first_tested_mean_reversal'] is None: note='No ABC-to-Spread mean crossover in tested range'
                else:
                    p=c['first_tested_mean_reversal']; ax.axvline(p,color=COLORS['Spread'],ls='--',alpha=.6); note=f'First tested mean reversal: {p} pickers; see paired CIs'
                ax.text(.02,.81,note,transform=ax.transAxes,fontsize=9,color='#344856')
            fig.text(.09,.015,'Bands: 95% t intervals across 10 replications. Model capacity, not observed warehouse output.',fontsize=8,color='#52616A')
            fig.tight_layout(rect=[0,.04,1,1]); fig.savefig(figs/f'{name}_{scope}.png'); fig.savefig(figs/f'{name}_{scope}.svg'); plt.close(fig)
    # Concentration knob.
    g=summary.loc[(summary.scope=='compact800')&summary.family.isin(['baseline','concentration'])]
    fig,ax=plt.subplots(figsize=(9.5,5.2))
    for pol in ['ABC','A50','A100','Spread']:
        d=g.loc[g.policy==pol].sort_values('pickers'); ax.errorbar(d.pickers,d.orders_per_hour,yerr=d.orders_per_hour_high-d.orders_per_hour,fmt='-o',label=pol,color=COLORS[pol],capsize=2)
    ax.set(xlabel='Pickers',ylabel='Orders / hour',title='Concentration is a design choice\n800-SKU compact scope | 3 orders/tour | S-shape'); ax.legend(frameon=False); ax.grid(axis='y',alpha=.2); fig.tight_layout(); fig.savefig(figs/'concentration.png'); plt.close(fig)
    # Paired headline differences, with simultaneous intervals.
    fig,axes=plt.subplots(1,2,figsize=(11,4.3))
    for ax,scope in zip(axes,['compact800','coverage90']):
        d=paired.loc[(paired.scope==scope)&(paired.family=='baseline')]
        ax.errorbar(d.pickers,d.spread_minus_abc,yerr=d.simultaneous_high-d.spread_minus_abc,fmt='o-',color=COLORS['Spread'],capsize=3)
        ax.axhline(0,color='#333',lw=1); ax.set(title=scope,xlabel='Pickers',ylabel='Spread minus ABC (orders/hour)'); ax.grid(axis='y',alpha=.2)
    fig.suptitle('Does spreading recover its travel penalty? 95% simultaneous intervals',fontweight='bold'); fig.tight_layout(); fig.savefig(figs/'paired_difference.png'); plt.close(fig)
    extra_analysis(summary,raw,results,figs,scopes)
    print(json.dumps(crossover,indent=2)); print(pd.DataFrame(economics).query('demand_multiplier==1').to_string(index=False))
    return summary

def extra_analysis(summary,raw,results,figs,scopes):
    economics=[]
    for scope in scopes.scope:
        demand=float(scopes.loc[scopes.scope==scope,'demand_orders_hour'].iloc[0])
        for pol in ['ABC','Spread']:
            for k in [3,5]:
                cap=summary.loc[(summary.scope==scope)&(summary.policy==pol)&(summary.k==k)&summary.family.isin(['baseline','batching','batching_grid'])].sort_values('pickers')
                ok=cap.loc[cap.orders_per_hour_low>=demand/.85]
                if len(ok):
                    r=ok.iloc[0]; p=int(r.pickers)
                    actual=summary.loc[(summary.scope==scope)&(summary.policy==pol)&(summary.k==k)&(summary.pickers==p)&summary.family.isin(['demand','demand_k5'])].iloc[0]
                    economics.append(dict(scope=scope,policy=pol,k=k,demand_orders_hour=demand,pickers=p,capacity_lower=r.orders_per_hour_low,nominal_labor_hours_1000=1000*p/demand,simulated_labor_hours_1000=actual.labor_hours_per_1000,simulated_labor_low=actual.labor_hours_per_1000_low,simulated_labor_high=actual.labor_hours_per_1000_high,illustrative_dollars_1000=25*actual.labor_hours_per_1000,utilization=actual.utilization,oldest_order_minutes=actual.mean_oldest_order_seconds/60,mean_queue_minutes=actual.mean_queue_seconds/60,wip_change=actual.wip_end-actual.wip_start))
    pd.DataFrame(economics).to_csv(results/'batch_staffing_economics.csv',index=False)
    components=raw.loc[raw.family=='blocking_components'].groupby(['scope','policy','pickers'])[['blocking_hours','gate_blocking_hours','cell_blocking_hours']].mean().reset_index()
    components['gate_share_of_blocking']=components.gate_blocking_hours/components.blocking_hours
    components.to_csv(results/'blocking_components.csv',index=False)
    density=raw.loc[raw.family=='density_extension']; pairs=[]
    for p,g in density.groupby('pickers'):
        v=g.pivot(index='rep',columns='policy',values='orders_per_hour'); m,l,h=interval(v.Spread-v.ABC)
        pairs.append(dict(pickers=p,pickers_per_10_aisles=p*10/115,spread_minus_abc=m,ci_low=l,ci_high=h))
    pd.DataFrame(pairs).to_csv(results/'density_paired.csv',index=False)
    if len(density):
        fig,ax=plt.subplots(figsize=(9.5,5.2))
        for pol in ['ABC','Spread']:
            d=summary.loc[(summary.scope=='coverage90')&(summary.policy==pol)&summary.family.isin(['baseline','density_extension'])].sort_values('pickers')
            ax.plot(d.pickers*10/115,d.orders_per_hour,'-o',label=pol,color=COLORS[pol])
            ax.fill_between(d.pickers*10/115,d.orders_per_hour_low,d.orders_per_hour_high,alpha=.15,color=COLORS[pol])
        ax.set(xlabel='Pickers per 10 aisles (115 total aisles)',ylabel='Orders / hour',title='Density extension: staffing the larger layout comparably'); ax.legend(frameon=False); ax.grid(axis='y',alpha=.2); fig.tight_layout(); fig.savefig(figs/'density_extension.png'); plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    for ax,scope in zip(axes,['compact800','coverage90']):
        for pol in ['ABC','Spread']:
            d=summary.loc[(summary.scope==scope)&(summary.policy==pol)&(summary.pickers==20)&summary.family.isin(['baseline','batching'])].sort_values('k')
            ax.errorbar(d.k,d.orders_per_hour,yerr=d.orders_per_hour_high-d.orders_per_hour,fmt='-o',label=pol,color=COLORS[pol],capsize=3)
        ax.set(title=scope,xlabel='Orders per tour',ylabel='Orders / hour',xticks=[1,3,5]); ax.legend(frameon=False); ax.grid(axis='y',alpha=.2)
    fig.suptitle('Batching can reverse the slotting recommendation | 20 pickers',fontweight='bold'); fig.tight_layout(); fig.savefig(figs/'batching_tradeoff.png'); plt.close(fig)

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser(); a.add_argument('--root',default='.'); analyze(a.parse_args().root)
