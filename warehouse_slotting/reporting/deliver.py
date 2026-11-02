"""Build the offline dashboard, executed notebooks and decision documents."""
from pathlib import Path
import json,io,base64,contextlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.pagesizes import A4

INK='#18313D'; TEAL='#176B70'; ORANGE='#D16B38'

def mdtable(frame):
    def clean(v):
        if isinstance(v,(float,np.floating)): return f'{v:.2f}'
        return str(v)
    rows=[list(map(str,frame.columns))]+[[clean(x) for x in row] for row in frame.itertuples(index=False,name=None)]
    return '| '+' | '.join(rows[0])+' |\n| '+' | '.join(['---']*len(rows[0]))+' |\n'+'\n'.join('| '+' | '.join(r)+' |' for r in rows[1:])

def read(root):
    r=root/'results'
    return dict(summary=pd.read_csv(r/'summary.csv'),scopes=pd.read_csv(r/'scope_summary.csv'),economics=pd.read_csv(r/'batch_staffing_economics.csv'),travel=pd.read_csv(r/'paired_travel_comparisons.csv'),validation=json.loads((r/'validation.json').read_text()),density=pd.read_csv(r/'density_paired.csv'),components=pd.read_csv(r/'blocking_components.csv'))

def documents(root,data):
    s=data['summary']; e=data['economics']; best=e.query("scope=='coverage90' and policy=='ABC' and k==5").iloc[0]
    old=e.query("scope=='coverage90' and policy=='ABC' and k==3").iloc[0]
    (root/'README.md').write_text(f'''# Congestion-aware slotting: a conditional crossover, not a universal rule

**12 pickers per 10 aisles is the first tested mean crossover from ABC to Spread with three-order batches. A sustained advantage is supported from 16 pickers by simultaneous 95% intervals.** The interpolated point estimate is 10.34; it is not an estimated precise physical threshold. This compact experiment serves only 8.0% of sampled complete orders.

![Operating curve](figures/throughput_compact800.png)

In the 9,149-SKU, 115-aisle layout, ABC stays ahead through 20 total pickers. A density extension finds the first tested reversal at **138 total pickers, or 12 per ten aisles** (preceded by an ABC advantage at 92). Do not confuse these total headcounts. At ordinary scenario demand, five-order batching with ABC is the stronger operating choice.

## Decision

For the clearly labeled **33.1 eligible orders/hour** scenario in the larger layout, choose **ABC, five orders per tour, six pickers**, subject to acceptable batch lead time and vehicle capacity. This meets the tested lower-capacity-bound rule with 15% nominal reserve. Simulated paid labor is **{best.simulated_labor_hours_1000:.1f} hours per 1,000 orders** (95% CI {best.simulated_labor_low:.1f}-{best.simulated_labor_high:.1f}), or **${best.illustrative_dollars_1000:,.0f} per 1,000** at an illustrative $25/hour. Compared with eight pickers and three-order ABC batches, measured labor falls {100*(1-best.simulated_labor_hours_1000/old.simulated_labor_hours_1000):.1f}%, while mean oldest-order completion time rises from {old.oldest_order_minutes:.1f} to {best.oldest_order_minutes:.1f} minutes. There is no actual facility demand or wage in the dataset.

For the compact **152.3 eligible orders/hour** scenario, use eight pickers with five-order batches. ABC and Spread have essentially the same paid-labor requirement; ABC offers more capacity headroom and shorter tours. Spread's high-load three-order advantage is not a reason to spread all items at low staffing or under a different batch size.

## What the evidence says

- Training: 2,571,421 prior orders; validation split: 643,453. Velocity and SKU coverage use 25,944,305 training lines; no held-out orders train the layout.
- A uniform sample of 60,000 held-out orders yields 4,801 complete eligible compact orders and 31,816 larger-layout orders. Affinities use 120,000 training baskets.
- Single-order S-shape travel: ABC saves 26.2% versus random in the compact scope and 19.2% in the larger scope. Spread costs 16.1% and 20.6% more travel than ABC, respectively.
- At 20 compact-model pickers and k=3, Spread delivers 308.0 versus ABC's 283.1 orders/hour: +8.8% throughput and about 8.2% fewer capacity labor hours per 1,000. Blocking is 35.7% versus 47.6% of active time.
- At the same staffing with k=5, ABC delivers 410.0 versus Spread's 393.6 orders/hour. In the no-interference bound, ABC also stays ahead. The conclusion depends on batching and traffic rules.
- Approximately 76.6% of ABC's compact-scope blocking at 20 pickers is aisle-entry traffic control; 23.4% is waiting for occupied cells. This is a congestion result for the stated dispatch protocol, not proof that local in-aisle blocking alone causes the crossover.
- 2,900 replicated shifts across 290 cells; ten replications each. 320 direct single-picker checks match the independent analytic time model to numerical precision. Nine automated test methods include 24 exact backend comparisons. All runs pass time and order-flow conservation; none recycles its sampled batch stream.

## Open the deliverables

- [Two-page decision brief](report.pdf)
- [Offline interactive evidence explorer](dashboard.html)
- [Detailed results and decision tables](docs/RESULTS.md)
- [Model, assumptions, limitations and sources](docs/METHODS.md)
- [Reproduction instructions](docs/REPRODUCE.md)
- [Defensible resume bullets](docs/RESUME_BULLETS.md)
- [Executed data/scope notebook](notebooks/01_data_and_scope.ipynb)
- [Executed results notebook](notebooks/02_operating_curves.ipynb)
- [Blocking chart](figures/blocking_compact800.png), [batching tradeoff](figures/batching_tradeoff.png), [density extension](figures/density_extension.png), [concentration knob](figures/concentration.png)
- [Raw replication CSV](https://github.com/shawnslee1202/warehouse-slotting/blob/0fecc92dc044f413ccf9aba906f88bc311b50518/results/replications.csv), [supplemental CSV](https://github.com/shawnslee1202/warehouse-slotting/blob/0fecc92dc044f413ccf9aba906f88bc311b50518/results/supplemental_replications.csv), [all means and CIs](results/summary.csv), [validation audit](results/validation.json)

## Limits on the recommendation

The larger scope covers 90.0% of held-out lines but only 53.0% of complete orders. Excluding the rest shortens baskets from 10.10 to 7.75 lines on average. Tail orders need a separately costed process before this can represent a whole warehouse. The compact subset is much more selective (3.29 lines/order). Both layouts are assumed, including long travel to cold blocks. No dimensions, weights, quantities, cart capacities, actual storage temperatures, calendar dates or facility arrival rates are provided. Conservative exclusive returns and direction control matter; passing sensitivity is an optimistic no-interference bound. Confidence intervals describe simulation/order-sampling noise under fixed assumptions, not physical model uncertainty or customer-level generalization.

## Re-run

Install requirements.txt in a Python 3.12 virtual environment, then follow [REPRODUCE.md](docs/REPRODUCE.md). The code is organized as data download/preparation, layout, routing, SimPy simulation, experiment runner, analysis and artifact generation. Raw data are not included. The pinned public mirror and file hashes are recorded in [data_manifest.json](results/data_manifest.json).

Data attribution: *The Instacart Online Grocery Shopping Dataset 2017*, retrieved through the pinned public mirror on 2026-10-27. Original dataset terms remain applicable; this package is a noncommercial research artifact. Literature: [de Koster et al. (2007)](https://doi.org/10.1016/j.ejor.2006.07.009) and [Gue et al. (2006)](https://doi.org/10.1080/07408170600809341). Full source notes and the distinction between measured data and assumptions are in METHODS.md.
''',encoding='utf-8')
    tables=[]
    tables.append('# Results and operating recommendation\n\nAll throughput and cost results below are simulation outputs for eligible held-out baskets, not observed Instacart warehouse performance. Ten replications per cell; eight measured hours after warm-up.\n')
    tables.append('## Coverage and selection bias\n\n'+mdtable(data['scopes'])+'\n')
    tables.append('## Out-of-sample single-order travel\n\n'+mdtable(pd.read_csv(root/'results/single_picker_travel.csv'))+'\n')
    tables.append('## Paired comparison against ABC\n\nNegative throughput differences favor ABC. The simultaneous interval adjusts over the eight main staffing comparisons in each layout.\n\n'+mdtable(pd.read_csv(root/'results/paired_throughput.csv').query("family=='baseline'"))+'\n')
    tables.append('## Three-order capacity operating curves\n\n'+mdtable(s.query("family=='baseline'")[['scope','policy','pickers','orders_per_hour','orders_per_hour_low','orders_per_hour_high','blocking_share','labor_hours_per_1000']])+'\n')
    tables.append('## Demand-based staffing and paid labor\n\nChoose the smallest tested staffing level whose lower 95% capacity bound exceeds demand / 0.85. The same central demand is used for both batch sizes. Costs include paid idle time. Mean oldest-order time is a batch-leading-order metric, not the average individual-order lead time. Larger batches save labor but increase waiting/tour time; no customer-service target is supplied.\n\n'+mdtable(e)+'\n')
    tables.append('## Why the crossover is conditional\n\n'+mdtable(s.query("family in ['batching','routing','passing','warmup','pick_time','walk_speed'] and pickers==20")[['scope','policy','family','k','routing','passing','pick_seconds','speed','orders_per_hour','blocking_share']])+'\n')
    tables.append('## Blocking decomposition\n\nGate waiting includes directional traffic control and exclusive return excursions. Cell waiting is following an occupied position. These are not interchangeable mechanisms.\n\n'+mdtable(data['components'])+'\n')
    tables.append('## Larger-layout density extension\n\nThe larger layout has 115 aisles; comparing only 1-20 total pickers would test a much lower density than the compact layout. These additional runs use three-order S-shape tours and the same modeled traffic control. Paired intervals here are pointwise, not a new pre-specified simultaneous crossover test.\n\n'+mdtable(data['density'])+'\n')
    tables.append('## Validation\n\n```json\n'+json.dumps(data['validation'],indent=2)+'\n```\n\nSee tests/, verification.csv, data_integrity.json, and METHODS.md. The results are exploratory design evidence. Collect actual geometry, batch/cart limits, entry rules, passing observations, service times, tail-order handling and demand before a production decision. The optional Simio rebuild, middle cross aisle, re-slotting and seed-savings batching were not required for the three completed stages and are not claimed as implemented.\n')
    (root/'docs/RESULTS.md').write_text('\n'.join(tables),encoding='utf-8')
    (root/'docs/RESUME_BULLETS.md').write_text('''# Resume bullets supported by this project

- Built a congestion-aware warehouse model using 3.21M Instacart prior orders; trained slotting on an 80% order split and evaluated 9,149 SKUs on 31,816 eligible held-out baskets, measuring 19.2% less single-order travel for ABC than random storage.
- Designed and verified a SimPy cell-occupancy model; ran 2,900 replicated shifts and found a conditional ABC-to-Spread crossover at 12 pickers in a 10-aisle, three-order-batch scenario, with simultaneous confidence intervals supporting the advantage from 16 pickers.
- Converted simulated capacity into staffing and labor economics; recommended six pickers with five-order ABC batching for a labeled 33.1-order/hour scenario, yielding 183.2 paid labor hours per 1,000 eligible orders while quantifying the lead-time tradeoff.

Use only bullets you can explain and reproduce. Say “modeled,” “simulated,” and “scenario”; do not describe these as deployed savings or an observed Instacart operation. The compact scope retains 8.0% of complete sampled orders, the larger scope 53.0%, and entry-control queues drive much of the compact-model congestion. A short resume can use the first and third bullets and discuss the crossover during an interview.
''',encoding='utf-8')


def pdf(root,data):
    path=root/'report.pdf'; c=canvas.Canvas(str(path),pagesize=A4); W,H=A4; M=42; width=W-2*M
    c.setTitle('Congestion-aware slotting: decision brief'); c.setAuthor('Warehouse Slotting Project')
    styles={n:ParagraphStyle(n,fontName='Helvetica',fontSize=size,leading=lead,textColor=HexColor(INK)) for n,size,lead in [('body',9.5,13.3),('small',8,10.7),('h',14,18)]}
    def para(text,x,y,w,kind='body'):
        p=Paragraph(text,styles[kind]); _,h=p.wrap(w,H); p.drawOn(c,x,y-h); return y-h
    def heading(text,y):
        return para('<b>'+text+'</b>',M,y,width,'h')-9
    def footer(page):
        c.setStrokeColor(HexColor('#DCE5E8')); c.line(M,37,W-M,37); c.setFillColor(HexColor('#526773')); c.setFont('Helvetica',7.5); c.drawString(M,24,'Instacart 2017 baskets | Research simulation | 27 October 2026'); c.drawRightString(W-M,24,str(page)+' / 2')
    c.setFillColor(HexColor(TEAL)); c.rect(0,H-11,W,11,fill=1,stroke=0)
    c.setFillColor(HexColor(INK)); c.setFont('Helvetica-Bold',27); c.drawString(M,H-57,'Congestion-aware slotting')
    y=para('Concentrate first. Spread when staffing and operating rules justify it.',M,H-73,width,'h')-18
    kpis=[('12 pickers','first tested mean crossover*'),('16 pickers','sustained simultaneous evidence*'),('183.2 h','paid labor / 1,000 orders**')]
    gap=9; kw=(width-2*gap)/3
    for i,(value,label) in enumerate(kpis):
        x=M+i*(kw+gap); c.setFillColor(HexColor('#EEF4F4')); c.roundRect(x,y-66,kw,66,6,fill=1,stroke=0); c.setFillColor(HexColor(TEAL)); c.setFont('Helvetica-Bold',21); c.drawString(x+11,y-27,value); para(label,x+11,y-36,kw-20,'small')
    y-=78
    y=para('*10-aisle compact model, k=3, no passing with entry control. **Larger-layout demand scenario; see page 2.',M,y,width,'small')-9
    chart_h=width*5.2/9.5; c.drawImage(str(root/'figures/throughput_compact800.png'),M,y-chart_h,width,chart_h,mask='auto'); y-=chart_h+9
    y=heading('The result, and where it stops applying',y)
    y=para('At 20 compact-model pickers, Spread produces <b>308.0 vs. 283.1 orders/hour</b> for ABC (+8.8%), while blocking falls from <b>47.6% to 35.7%</b> of active time. It pays for 16.1% more single-order travel than ABC. The first positive tested paired mean is at 12 pickers; the simultaneous interval includes zero there and excludes zero from 16 onward. Do not report the interpolated 10.34 as a precise threshold.',M,y,width)-10
    y=para('The larger, 115-aisle layout has <b>no crossover through 20 total pickers</b>. Extending staffing to comparable density produces the first tested reversal at <b>138 pickers (12 per ten aisles)</b>, following an ABC advantage at 92. Density, not an unqualified total headcount, is the useful comparison.',M,y,width)-10
    y=para('<b>Critical scope limit:</b> top-800 storage covers 50.3% of held-out lines but only 8.0% of complete orders. The 9,149-SKU design covers 90.0% of lines and 53.0% of complete orders. Orders touching excluded items are excluded, not shortened. These curves do not price a complete warehouse with a long-tail process.',M,y,width)
    if y<50: raise RuntimeError(f'PDF page one overflow: {y}')
    footer(1); c.showPage()
    c.setFillColor(HexColor(TEAL)); c.rect(0,H-11,W,11,fill=1,stroke=0)
    y=heading('Operating recommendation: optimize batching first',H-43)
    y=para('At a labeled <b>33.1 eligible orders/hour</b> in the larger layout, select <b>ABC, k=5, six pickers</b>. Choose the smallest tested staffing whose lower 95% capacity bound exceeds demand / 0.85. There is no observed facility demand or wage; $25/hour is illustrative.',M,y,width)-12
    rows=[['Larger-layout option','Pickers','Paid h/1,000','Oldest-order min']]
    e=data['economics']
    for pol,k in [('ABC',3),('ABC',5),('Spread',5)]:
        r=e.query("scope=='coverage90'").loc[lambda d:(d.policy==pol)&(d.k==k)].iloc[0]
        rows.append([f'{pol}, {k} orders/tour',str(int(r.pickers)),f'{r.simulated_labor_hours_1000:.1f}',f'{r.oldest_order_minutes:.1f}'])
    table=Table(rows,colWidths=[185,60,120,width-365],rowHeights=25)
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor(INK)),('TEXTCOLOR',(0,0),(-1,0),white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),8.6),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#F1F6F6'),white]),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8)]))
    _,th=table.wrap(width,300); table.drawOn(c,M,y-th); y-=th+12
    y=para('ABC with k=5 yields <b>183.2 paid hours/1,000</b> (95% CI 177.3-189.1), or about <b>$4,580/1,000</b>. That is 24.5% less measured labor than k=3 ABC, but oldest-order completion rises by 13.1 minutes. This batch-leading-order metric is not mean individual-order lead time. At compact demand (152.3/hour), eight pickers with k=5 suffice; ABC provides more headroom than Spread at nearly equal paid labor.',M,y,width)-13
    y=heading('Why the recommendation is conditional',y)
    y=para('<b>Batching:</b> at 20 compact pickers, k=5 puts ABC back ahead: 410.0 vs. 393.6 orders/hour. <b>Passing:</b> removing all aisle interference also restores ABC\'s advantage. <b>Traffic control:</b> 76.6% of ABC\'s compact blocking at 20 pickers is entry-gate waiting. Exclusive return trips and direction changes are conservative dispatch assumptions, not measured site behavior.',M,y,width)-13
    y=heading('Model and verification',y)
    y=para('Training uses 2.57M orders in an 80/20 order-ID split; affinities use 120,000 training baskets. Of 60,000 sampled held-out orders, 31,816 are eligible in the larger layout. Four storage policies plus a concentration knob use temperature blocks and frozen-last routes. SimPy tracks travel, pick, entry/cell waiting and idle time; base assumptions are 1.2 m/s, 15 s/line and 30 s depot handling. Separate saturated-capacity and Poisson-demand runs prevent demand caps from hiding congestion.',M,y,width)-8
    y=para('<b>Checks:</b> 2,900 replicated shifts, 290 cells, ten seeds per cell; one-hour warm-up plus eight measured hours, with a two-hour sensitivity. All 320 one-picker checks agree with independent analytic distances/times to numerical precision. Nine test methods include 24 reference-vs-optimized backend comparisons. Time and order-flow conservation pass. Bands reflect replication uncertainty under fixed assumptions.',M,y,width)-12
    y=heading('Limits before using this in an operation',y)
    y=para('Geometry, storage temperatures and traffic rules are assumed. There are no weights, volumes, quantities, cart capacities, calendar dates or facility demand. Long-tail work, refrigeration, replenishment, breaks, errors and relocation costs are excluded. Order-level holdout does not isolate customers. Collect actual travel/service times, passing and return rules, batch limits, demand and tail-order costs before deploying a policy.',M,y,width)-11
    y=para('<b>Sources:</b> Instacart Online Grocery Shopping Dataset 2017; pinned public mirror and hashes in results/data_manifest.json. de Koster et al. (2007), EJOR 182:481-501, doi:10.1016/j.ejor.2006.07.009 (framing). Gue et al. (2006), IIE Transactions 38:859-868, doi:10.1080/07408170600809341 (blocking motivation; author manuscript consulted). Full assumptions, references, code and results accompany this brief.',M,y,width,'small')
    if y<50: raise RuntimeError(f'PDF page two overflow: {y}')
    footer(2); c.save()


def notebook(root,name,title,codes):
    cells=[dict(cell_type='markdown',metadata={},source=[f'# {title}\n','Executed against the delivered CSV results. See ../docs/METHODS.md for model assumptions.'])]; env={}
    for i,code in enumerate(codes,1):
        out=io.StringIO()
        with contextlib.redirect_stdout(out): exec(code,env)
        outputs=[]
        if out.getvalue(): outputs.append(dict(output_type='stream',name='stdout',text=out.getvalue().splitlines(True)))
        for f in plt.get_fignums():
            fig=plt.figure(f); b=io.BytesIO(); fig.savefig(b,format='png',dpi=120,bbox_inches='tight'); outputs.append(dict(output_type='display_data',metadata={},data={'image/png':base64.b64encode(b.getvalue()).decode()})); plt.close(fig)
        cells.append(dict(cell_type='code',execution_count=i,metadata={},source=code.splitlines(True),outputs=outputs))
    nb=dict(nbformat=4,nbformat_minor=5,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},cells=cells)
    # Stable unique IDs are required by notebook format 4.5.
    for i,cell in enumerate(cells): cell['id']=f'cell-{i:03d}'
    (root/'notebooks'/name).write_text(json.dumps(nb,indent=1),encoding='utf-8')


def notebooks(root):
    import os
    old=Path.cwd(); os.chdir(root/'notebooks')
    try:
        notebook(root,'01_data_and_scope.ipynb','Data provenance, coverage and selection',[
            "from pathlib import Path\nimport json\nimport pandas as pd\nimport matplotlib.pyplot as plt\nroot=Path('..')\nprint(json.loads((root/'results/data_integrity.json').read_text()))\n",
            "scope=pd.read_csv(root/'results/scope_summary.csv')\nprint(scope[['scope','skus','train_line_coverage','heldout_line_coverage','heldout_complete_order_fraction','eligible_heldout_orders','mean_lines_all','mean_lines_eligible']].to_string(index=False))\n",
            "fig,ax=plt.subplots(figsize=(8,4))\nscope.set_index('scope')[['heldout_line_coverage','heldout_complete_order_fraction']].plot.bar(ax=ax,color=['#176b70','#d16b38'])\nax.set(ylabel='Fraction retained',title='Line coverage does not equal complete-order coverage')\nax.tick_params(axis='x',rotation=0)\nfig.tight_layout()\n",
            "velocity=pd.read_csv(root/'results/sku_velocity.csv')\nprint(velocity[['product_id','product_name','zone','train_lines']].head(12).to_string(index=False))\nprint('All slotting ranks use training lines only; eligibility selection is disclosed, not used to retune storage.')\n"
        ])
        notebook(root,'02_operating_curves.ipynb','Operating curves, crossover and labor economics',[
            "from pathlib import Path\nimport json\nimport pandas as pd\nimport matplotlib.pyplot as plt\nroot=Path('..')\ns=pd.read_csv(root/'results/summary.csv')\nprint(json.loads((root/'results/validation.json').read_text()))\n",
            "d=s.query(\"scope=='compact800' and family=='baseline'\")\nfig,ax=plt.subplots(figsize=(9,4.5))\ncolors={'ABC':'#176b70','Spread':'#d16b38','Affinity':'#7961a5','Random':'#9aadb8'}\nfor policy,g in d.groupby('policy'):\n    g=g.sort_values('pickers')\n    ax.errorbar(g.pickers,g.orders_per_hour,yerr=g.orders_per_hour_high-g.orders_per_hour,fmt='-o',label=policy,color=colors[policy],capsize=3)\nax.set(xlabel='Pickers',ylabel='Orders/hour',title='Compact capacity: three orders per tour')\nax.legend(); fig.tight_layout()\n",
            "paired=pd.read_csv(root/'results/paired_throughput.csv')\nprint(paired.query(\"scope=='compact800' and family=='baseline'\").to_string(index=False))\nprint('At 12 pickers the pointwise interval is positive, but the simultaneous interval includes zero. Sustained simultaneous evidence begins at 16.')\n",
            "economics=pd.read_csv(root/'results/batch_staffing_economics.csv')\nprint(economics[['scope','policy','k','pickers','simulated_labor_hours_1000','simulated_labor_low','simulated_labor_high','oldest_order_minutes']].round(2).to_string(index=False))\n",
            "print(pd.read_csv(root/'results/density_paired.csv').round(3).to_string(index=False))\nprint('115-aisle extension: 138 total pickers equals 12 pickers per ten aisles. Do not equate it with 12 total pickers.')\n"
        ])
    finally: os.chdir(old)


def dashboard(root,data):
    payload={'summary':json.loads(data['summary'].to_json(orient='records')),'scopes':json.loads(data['scopes'].to_json(orient='records'))}
    template=(Path(__file__).with_name('dashboard_template.html')).read_text(encoding='utf-8-sig')
    (root/'dashboard.html').write_text(template.replace('__DATA__',json.dumps(payload,separators=(',',':'))),encoding='utf-8')


def deliver(root):
    root=Path(root).resolve(); data=read(root); documents(root,data); dashboard(root,data); notebooks(root); pdf(root,data)
    print('Created report.pdf, dashboard.html, README, detailed results, resume bullets and two executed notebooks.')

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser(); a.add_argument('--root',default='.'); deliver(a.parse_args().root)
