# Congestion-aware slotting: a conditional crossover, not a universal rule

**12 pickers per 10 aisles is the first tested mean crossover from ABC to Spread with three-order batches. A sustained advantage is supported from 16 pickers by simultaneous 95% intervals.** The interpolated point estimate is 10.34; it is not an estimated precise physical threshold. This compact experiment serves only 8.0% of sampled complete orders.

![Operating curve](figures/throughput_compact800.png)

In the 9,149-SKU, 115-aisle layout, ABC stays ahead through 20 total pickers. A density extension finds the first tested reversal at **138 total pickers, or 12 per ten aisles** (preceded by an ABC advantage at 92). Do not confuse these total headcounts. At ordinary scenario demand, five-order batching with ABC is the stronger operating choice.

## Decision

For the clearly labeled **33.1 eligible orders/hour** scenario in the larger layout, choose **ABC, five orders per tour, six pickers**, subject to acceptable batch lead time and vehicle capacity. This meets the tested lower-capacity-bound rule with 15% nominal reserve. Simulated paid labor is **183.2 hours per 1,000 orders** (95% CI 177.3-189.1), or **$4,580 per 1,000** at an illustrative $25/hour. Compared with eight pickers and three-order ABC batches, measured labor falls 24.5%, while mean oldest-order completion time rises from 34.3 to 47.4 minutes. There is no actual facility demand or wage in the dataset.

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
