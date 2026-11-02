# Results data dictionary

All time quantities are seconds unless a column name specifies hours or minutes. Every throughput observation is based on completions within the eight-hour measurement window after warm-up. All policies in a scope use the same eligible held-out order population.

The experiment regenerates the per-shift records, slot assignments, pair counts and aisle workloads locally. [Original run files](https://github.com/shawnslee1202/warehouse-slotting/tree/0fecc92dc044f413ccf9aba906f88bc311b50518/results) remain available.

| File | Grain and purpose |
| --- | --- |
| data_manifest.json | Pinned source URL, byte size and SHA-256 for each raw CSV |
| data_integrity.json | Full-prior-table row counts, key, duplicate and missing-value audit |
| data_summary.json | Training/holdout population and sampling seeds |
| scope_summary.csv | SKU coverage, complete-order retention, geometry and scenario demand for each scope |
| sku_velocity.csv | All product velocities from training data only; rank order determines scoping |
| order_time_profile.csv | Prior orders by supplied day-of-week code and hour; relative shopping activity only, not warehouse demand |
| top_affinities_*.csv | Top 5,000 unordered product pairs by co-occurrence in sampled training orders, within the scoped catalog; slotting additionally enforces zones |
| slotting_*.csv | Product-to-zone/aisle/depth/side assignment for each fixed policy |
| aisle_workload_*.csv | Training lines per aisle and share of the scoped training workload |
| layout_*.json | Zone-to-aisle mapping, depth, pitch, spacing and nominal width |
| single_picker_travel.csv | Mean analytic meters per single order, with order-level 95% t intervals |
| paired_travel_comparisons.csv | Paired travel differences versus ABC and descriptive ratio savings |
| verification.csv | One-picker distance and service-time comparisons on 320 held-out cases |
| experiment_design.csv | 216 main factor cells |
| supplemental_design.csv | 74 follow-up factor cells: density, blocking decomposition and k=5 staffing |
| replications.csv | 2,160 main replicated shifts |
| supplemental_replications.csv | 740 supplemental shifts, including gate/cell waiting decomposition |
| summary.csv | Mean and pointwise 95% t intervals by complete factor cell |
| paired_throughput.csv | Within-seed Spread minus ABC comparisons; pointwise and simultaneous intervals |
| crossovers.json | First tested mean reversal, descriptive linear interpolation, sustained simultaneous evidence |
| density_paired.csv | Paired larger-layout differences at comparable staffing density; pointwise intervals |
| staffing_economics.csv | Four-policy k=3 capacity-planning scenarios at 0.5x/1x/1.5x/2x central demand |
| batch_staffing_economics.csv | ABC/Spread comparison for k=3 and k=5, with actually simulated central demand |
| blocking_components.csv | Mean entry-control and occupied-cell waiting at 8/20 pickers |
| validation.json | Model-result audit assertions and replication completeness |


## Replication fields

- `scope`: `compact800` or `coverage90`. These retain different order populations; never compare their absolute rates as a controlled layout-only treatment.
- `policy`: Random, ABC, Affinity, Spread, A50 or A100. Storage randomization is fixed; uncertainty is conditional on that assignment.
- `k`, `routing`, `passing`, `warmup`, `speed`, `pick_seconds`, `pickers`: explicit model factors.
- `mode`: `capacity` means saturated backlog; `demand` means Poisson arrivals at `arrival_rate` orders/hour.
- `rep`, `seed`: independent replication index and arrival seed. Basket draws use 10000+rep; arrivals use 20000+rep.
- `family`: design grouping, not another physical factor. Baseline is k=3/S-shape/no-passing capacity; supplement diagnostics may repeat the same physical case intentionally under a different family.
- `orders_per_hour`, `lines_per_hour`: measured completed work divided by eight hours.
- `orders_completed`, `tours_completed`: measurement-window completions, without draining WIP.
- `mean_tour_seconds`: complete picker tour, including blocking and 30 seconds depot handling.
- `mean_queue_seconds`: ready batch to picker start; excludes order accumulation into a batch.
- `mean_oldest_order_seconds`: first order in a batch to completed tour. It is not the average lead time of every order in the batch.
- `blocking_share`: blocking seconds / active seconds, where active includes travel, picking, blocking and depot handling.
- `utilization`: active time / paid picker time; blocking is included. Saturated utilization is one by construction.
- `productive_utilization`: (travel + picking + depot) / paid time; a descriptive nonblocked fraction, not value-added utilization.
- `travel_hours`, `pick_hours`, `blocking_hours`, `idle_hours`, `depot_hours`: totals across all pickers, clipped to the eight-hour window. Sum equals pickers * 8.
- `gate_blocking_hours`, `cell_blocking_hours`: components of blocking, reported in supplemental replications and fresh reproductions. The original main CSV predates the diagnostic columns but uses the identical traffic logic.
- `labor_hours_per_1000`: 1000 * pickers * 8 / completed orders. Mean replication-level ratios need not exactly equal the ratio of average counts.
- `wip_start`, `wip_end`, `arrivals_window`: all uncompleted demand orders, including unbatched, queued and active orders. Start WIP + arrivals - completions = end WIP.
- `batches_started`, `stream_recycled`: audit of the 4,096-batch sampled stream. Recycling is false in all delivered runs.

The nominal staffing-cost calculation assumes throughput equals the chosen demand. The measured cost uses actual eight-hour completions; these differ slightly because of sampled arrivals and WIP. No staffing beyond a tested cell is interpolated in the recommendation. A missing feasible staffing level means not established within the grid, not impossible.
