# Results and operating recommendation

All throughput and cost results below are simulation outputs for eligible held-out baskets, not observed Instacart warehouse performance. Ten replications per cell; eight measured hours after warm-up.

## Coverage and selection bias

| scope | skus | train_line_coverage | heldout_line_coverage | heldout_complete_order_fraction | heldout_orders_before_exclusion | eligible_heldout_orders | mean_lines_all | mean_lines_eligible | aisles | slots_per_side | capacity | aisle_length_m | demand_orders_hour |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| compact800 | 800 | 0.50 | 0.50 | 0.08 | 60000 | 4801 | 10.10 | 3.29 | 10 | 46 | 920 | 47.00 | 152.30 |
| coverage90 | 9149 | 0.90 | 0.90 | 0.53 | 60000 | 31816 | 10.10 | 7.75 | 115 | 40 | 9200 | 41.00 | 33.10 |

## Out-of-sample single-order travel

| scope | policy | routing | n | meters_per_order | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- |
| compact800 | Random | s_shape | 4801 | 183.98 | 181.23 | 186.72 |
| compact800 | Random | largest_gap | 4801 | 170.74 | 168.43 | 173.04 |
| compact800 | ABC | s_shape | 4801 | 135.82 | 133.69 | 137.95 |
| compact800 | ABC | largest_gap | 4801 | 131.96 | 130.00 | 133.92 |
| compact800 | Affinity | s_shape | 4801 | 137.70 | 135.59 | 139.81 |
| compact800 | Affinity | largest_gap | 4801 | 133.60 | 131.67 | 135.53 |
| compact800 | Spread | s_shape | 4801 | 157.67 | 155.02 | 160.31 |
| compact800 | Spread | largest_gap | 4801 | 146.89 | 144.69 | 149.10 |
| coverage90 | Random | s_shape | 31816 | 1252.92 | 1247.48 | 1258.37 |
| coverage90 | Random | largest_gap | 31816 | 1178.06 | 1173.33 | 1182.78 |
| coverage90 | ABC | s_shape | 31816 | 1012.79 | 1008.19 | 1017.40 |
| coverage90 | ABC | largest_gap | 31816 | 973.68 | 969.45 | 977.91 |
| coverage90 | Affinity | s_shape | 31816 | 1029.87 | 1025.19 | 1034.55 |
| coverage90 | Affinity | largest_gap | 31816 | 991.06 | 986.76 | 995.36 |
| coverage90 | Spread | s_shape | 31816 | 1221.76 | 1216.28 | 1227.25 |
| coverage90 | Spread | largest_gap | 31816 | 1121.02 | 1116.56 | 1125.49 |

## Paired comparison against ABC

Negative throughput differences favor ABC. The simultaneous interval adjusts over the eight main staffing comparisons in each layout.

| scope | family | pickers | spread_minus_abc | ci_low | ci_high | simultaneous_low | simultaneous_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| compact800 | baseline | 1 | -3.04 | -3.43 | -2.65 | -3.65 | -2.43 |
| compact800 | baseline | 2 | -5.55 | -6.22 | -4.88 | -6.60 | -4.50 |
| compact800 | baseline | 4 | -8.06 | -8.83 | -7.29 | -9.27 | -6.85 |
| compact800 | baseline | 6 | -8.10 | -9.33 | -6.87 | -10.02 | -6.18 |
| compact800 | baseline | 8 | -6.90 | -9.22 | -4.58 | -10.53 | -3.27 |
| compact800 | baseline | 12 | 4.88 | 0.57 | 9.18 | -1.87 | 11.62 |
| compact800 | baseline | 16 | 14.59 | 8.57 | 20.60 | 5.16 | 24.02 |
| compact800 | baseline | 20 | 24.90 | 16.79 | 33.01 | 12.19 | 37.61 |
| coverage90 | baseline | 1 | -1.12 | -1.34 | -0.91 | -1.47 | -0.78 |
| coverage90 | baseline | 2 | -2.10 | -2.44 | -1.76 | -2.63 | -1.57 |
| coverage90 | baseline | 4 | -3.64 | -3.86 | -3.42 | -3.98 | -3.29 |
| coverage90 | baseline | 6 | -5.62 | -6.13 | -5.12 | -6.42 | -4.83 |
| coverage90 | baseline | 8 | -7.50 | -7.97 | -7.03 | -8.24 | -6.76 |
| coverage90 | baseline | 12 | -10.57 | -11.39 | -9.76 | -11.86 | -9.29 |
| coverage90 | baseline | 16 | -14.47 | -15.36 | -13.59 | -15.87 | -13.08 |
| coverage90 | baseline | 20 | -17.48 | -17.98 | -16.97 | -18.27 | -16.68 |

## Three-order capacity operating curves

| scope | policy | pickers | orders_per_hour | orders_per_hour_low | orders_per_hour_high | blocking_share | labor_hours_per_1000 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| compact800 | ABC | 1 | 27.07 | 26.61 | 27.54 | 0.00 | 36.95 |
| compact800 | ABC | 2 | 52.95 | 52.08 | 53.82 | 0.02 | 37.79 |
| compact800 | ABC | 4 | 99.83 | 99.03 | 100.62 | 0.08 | 40.07 |
| compact800 | ABC | 6 | 140.40 | 138.83 | 141.97 | 0.13 | 42.74 |
| compact800 | ABC | 8 | 175.54 | 173.61 | 177.47 | 0.19 | 45.58 |
| compact800 | ABC | 12 | 226.39 | 223.58 | 229.19 | 0.30 | 53.02 |
| compact800 | ABC | 16 | 261.71 | 257.60 | 265.82 | 0.39 | 61.16 |
| compact800 | ABC | 20 | 283.12 | 276.06 | 290.19 | 0.48 | 70.71 |
| compact800 | Affinity | 1 | 26.74 | 26.23 | 27.24 | 0.00 | 37.42 |
| compact800 | Affinity | 2 | 52.35 | 51.63 | 53.07 | 0.02 | 38.22 |
| compact800 | Affinity | 4 | 98.70 | 97.75 | 99.65 | 0.08 | 40.53 |
| compact800 | Affinity | 6 | 139.61 | 138.04 | 141.18 | 0.13 | 42.99 |
| compact800 | Affinity | 8 | 172.95 | 171.36 | 174.54 | 0.19 | 46.26 |
| compact800 | Affinity | 12 | 222.15 | 219.71 | 224.59 | 0.31 | 54.03 |
| compact800 | Affinity | 16 | 254.81 | 251.04 | 258.59 | 0.40 | 62.82 |
| compact800 | Affinity | 20 | 275.25 | 270.20 | 280.30 | 0.49 | 72.70 |
| compact800 | Random | 1 | 22.73 | 22.16 | 23.29 | 0.00 | 44.05 |
| compact800 | Random | 2 | 44.40 | 43.68 | 45.12 | 0.02 | 45.07 |
| compact800 | Random | 4 | 85.58 | 84.55 | 86.60 | 0.06 | 46.75 |
| compact800 | Random | 6 | 121.35 | 120.45 | 122.25 | 0.11 | 49.45 |
| compact800 | Random | 8 | 151.76 | 149.83 | 153.69 | 0.16 | 52.73 |
| compact800 | Random | 12 | 194.36 | 190.12 | 198.61 | 0.29 | 61.79 |
| compact800 | Random | 16 | 214.24 | 209.60 | 218.87 | 0.41 | 74.75 |
| compact800 | Random | 20 | 221.03 | 216.50 | 225.55 | 0.51 | 90.56 |
| compact800 | Spread | 1 | 24.04 | 23.37 | 24.70 | 0.00 | 41.66 |
| compact800 | Spread | 2 | 47.40 | 46.80 | 48.00 | 0.02 | 42.21 |
| compact800 | Spread | 4 | 91.76 | 90.98 | 92.54 | 0.05 | 43.60 |
| compact800 | Spread | 6 | 132.30 | 130.91 | 133.69 | 0.08 | 45.36 |
| compact800 | Spread | 8 | 168.64 | 166.99 | 170.28 | 0.12 | 47.45 |
| compact800 | Spread | 12 | 231.26 | 228.32 | 234.21 | 0.20 | 51.90 |
| compact800 | Spread | 16 | 276.30 | 272.74 | 279.86 | 0.28 | 57.92 |
| compact800 | Spread | 20 | 308.02 | 304.21 | 311.84 | 0.36 | 64.95 |
| coverage90 | ABC | 1 | 6.15 | 5.79 | 6.51 | 0.00 | 163.56 |
| coverage90 | ABC | 2 | 12.00 | 11.49 | 12.51 | 0.00 | 167.19 |
| coverage90 | ABC | 4 | 23.44 | 22.79 | 24.09 | 0.00 | 170.91 |
| coverage90 | ABC | 6 | 35.33 | 34.66 | 35.99 | 0.01 | 169.96 |
| coverage90 | ABC | 8 | 47.21 | 46.42 | 48.01 | 0.01 | 169.53 |
| coverage90 | ABC | 12 | 70.01 | 69.15 | 70.87 | 0.02 | 171.44 |
| coverage90 | ABC | 16 | 93.30 | 92.51 | 94.09 | 0.02 | 171.51 |
| coverage90 | ABC | 20 | 115.99 | 115.18 | 116.80 | 0.03 | 172.45 |
| coverage90 | Affinity | 1 | 6.15 | 5.84 | 6.46 | 0.00 | 163.36 |
| coverage90 | Affinity | 2 | 11.78 | 11.28 | 12.27 | 0.00 | 170.38 |
| coverage90 | Affinity | 4 | 23.02 | 22.47 | 23.58 | 0.00 | 173.91 |
| coverage90 | Affinity | 6 | 34.54 | 33.82 | 35.26 | 0.01 | 173.86 |
| coverage90 | Affinity | 8 | 46.42 | 45.83 | 47.02 | 0.01 | 172.37 |
| coverage90 | Affinity | 12 | 69.00 | 68.19 | 69.81 | 0.02 | 173.96 |
| coverage90 | Affinity | 16 | 91.88 | 90.75 | 93.00 | 0.02 | 174.20 |
| coverage90 | Affinity | 20 | 114.56 | 113.70 | 115.42 | 0.03 | 174.59 |
| coverage90 | Random | 1 | 4.99 | 4.63 | 5.35 | 0.00 | 202.41 |
| coverage90 | Random | 2 | 9.71 | 9.37 | 10.06 | 0.00 | 206.41 |
| coverage90 | Random | 4 | 19.57 | 19.03 | 20.12 | 0.00 | 204.63 |
| coverage90 | Random | 6 | 29.25 | 28.44 | 30.06 | 0.00 | 205.41 |
| coverage90 | Random | 8 | 39.19 | 38.20 | 40.18 | 0.00 | 204.38 |
| coverage90 | Random | 12 | 58.95 | 58.14 | 59.76 | 0.01 | 203.63 |
| coverage90 | Random | 16 | 77.92 | 76.85 | 79.00 | 0.01 | 205.39 |
| coverage90 | Random | 20 | 97.31 | 96.20 | 98.42 | 0.01 | 205.57 |
| coverage90 | Spread | 1 | 5.03 | 4.66 | 5.39 | 0.00 | 200.95 |
| coverage90 | Spread | 2 | 9.90 | 9.59 | 10.21 | 0.00 | 202.39 |
| coverage90 | Spread | 4 | 19.80 | 19.16 | 20.44 | 0.00 | 202.41 |
| coverage90 | Spread | 6 | 29.70 | 29.02 | 30.38 | 0.00 | 202.20 |
| coverage90 | Spread | 8 | 39.71 | 38.93 | 40.50 | 0.00 | 201.58 |
| coverage90 | Spread | 12 | 59.44 | 58.49 | 60.39 | 0.01 | 201.98 |
| coverage90 | Spread | 16 | 78.83 | 77.74 | 79.91 | 0.01 | 203.05 |
| coverage90 | Spread | 20 | 98.51 | 97.63 | 99.40 | 0.01 | 203.05 |

## Demand-based staffing and paid labor

Choose the smallest tested staffing level whose lower 95% capacity bound exceeds demand / 0.85. The same central demand is used for both batch sizes. Costs include paid idle time. Mean oldest-order time is a batch-leading-order metric, not the average individual-order lead time. Larger batches save labor but increase waiting/tour time; no customer-service target is supplied.

| scope | policy | k | demand_orders_hour | pickers | capacity_lower | nominal_labor_hours_1000 | simulated_labor_hours_1000 | simulated_labor_low | simulated_labor_high | illustrative_dollars_1000 | utilization | oldest_order_minutes | mean_queue_minutes | wip_change |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| compact800 | ABC | 3 | 152.30 | 12 | 223.58 | 78.79 | 79.69 | 78.21 | 81.17 | 1992.25 | 0.54 | 8.62 | 0.01 | -1.50 |
| compact800 | ABC | 5 | 152.30 | 8 | 219.97 | 52.53 | 53.03 | 52.06 | 54.01 | 1325.83 | 0.63 | 11.61 | 0.02 | -3.60 |
| compact800 | Spread | 3 | 152.30 | 12 | 228.32 | 78.79 | 79.73 | 78.30 | 81.15 | 1993.15 | 0.58 | 9.15 | 0.01 | -0.90 |
| compact800 | Spread | 5 | 152.30 | 8 | 203.19 | 52.53 | 52.92 | 51.94 | 53.91 | 1323.11 | 0.70 | 12.75 | 0.06 | -6.10 |
| coverage90 | ABC | 3 | 33.10 | 8 | 46.42 | 241.69 | 242.77 | 235.93 | 249.61 | 6069.29 | 0.70 | 34.33 | 0.19 | 0.00 |
| coverage90 | ABC | 5 | 33.10 | 6 | 43.76 | 181.27 | 183.20 | 177.33 | 189.07 | 4580.07 | 0.74 | 47.40 | 0.26 | 1.50 |
| coverage90 | Spread | 3 | 33.10 | 12 | 58.49 | 362.54 | 365.97 | 354.30 | 377.65 | 9149.31 | 0.56 | 39.90 | 0.00 | 1.20 |
| coverage90 | Spread | 5 | 33.10 | 8 | 48.50 | 241.69 | 245.73 | 237.41 | 254.04 | 6143.15 | 0.66 | 55.05 | 0.01 | 3.00 |

## Why the crossover is conditional

| scope | policy | family | k | routing | passing | pick_seconds | speed | orders_per_hour | blocking_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| compact800 | ABC | batching | 1 | s_shape | False | 15 | 1.20 | 107.65 | 0.71 |
| compact800 | ABC | routing | 3 | largest_gap | False | 15 | 1.20 | 264.75 | 0.53 |
| compact800 | ABC | walk_speed | 3 | s_shape | False | 15 | 1.00 | 261.49 | 0.46 |
| compact800 | ABC | pick_time | 3 | s_shape | False | 10 | 1.20 | 348.45 | 0.43 |
| compact800 | ABC | pick_time | 3 | s_shape | False | 20 | 1.20 | 235.35 | 0.51 |
| compact800 | ABC | walk_speed | 3 | s_shape | False | 15 | 1.30 | 292.65 | 0.48 |
| compact800 | ABC | warmup | 3 | s_shape | False | 15 | 1.20 | 284.48 | 0.47 |
| compact800 | ABC | passing | 3 | s_shape | True | 15 | 1.20 | 540.04 | 0.00 |
| compact800 | ABC | batching | 5 | s_shape | False | 15 | 1.20 | 410.00 | 0.36 |
| compact800 | Spread | batching | 1 | s_shape | False | 15 | 1.20 | 220.16 | 0.36 |
| compact800 | Spread | routing | 3 | largest_gap | False | 15 | 1.20 | 275.21 | 0.47 |
| compact800 | Spread | walk_speed | 3 | s_shape | False | 15 | 1.00 | 280.01 | 0.35 |
| compact800 | Spread | pick_time | 3 | s_shape | False | 10 | 1.20 | 367.39 | 0.32 |
| compact800 | Spread | pick_time | 3 | s_shape | False | 20 | 1.20 | 267.11 | 0.38 |
| compact800 | Spread | walk_speed | 3 | s_shape | False | 15 | 1.30 | 321.45 | 0.36 |
| compact800 | Spread | warmup | 3 | s_shape | False | 15 | 1.20 | 308.06 | 0.36 |
| compact800 | Spread | passing | 3 | s_shape | True | 15 | 1.20 | 480.52 | 0.00 |
| compact800 | Spread | batching | 5 | s_shape | False | 15 | 1.20 | 393.56 | 0.32 |
| coverage90 | ABC | batching | 1 | s_shape | False | 15 | 1.20 | 70.62 | 0.03 |
| coverage90 | ABC | routing | 3 | largest_gap | False | 15 | 1.20 | 121.20 | 0.05 |
| coverage90 | ABC | passing | 3 | s_shape | True | 15 | 1.20 | 119.47 | 0.00 |
| coverage90 | ABC | batching | 5 | s_shape | False | 15 | 1.20 | 144.62 | 0.03 |
| coverage90 | Spread | batching | 1 | s_shape | False | 15 | 1.20 | 61.50 | 0.01 |
| coverage90 | Spread | routing | 3 | largest_gap | False | 15 | 1.20 | 115.99 | 0.01 |
| coverage90 | Spread | passing | 3 | s_shape | True | 15 | 1.20 | 99.67 | 0.00 |
| coverage90 | Spread | batching | 5 | s_shape | False | 15 | 1.20 | 121.75 | 0.02 |

## Blocking decomposition

Gate waiting includes directional traffic control and exclusive return excursions. Cell waiting is following an occupied position. These are not interchangeable mechanisms.

| scope | policy | pickers | blocking_hours | gate_blocking_hours | cell_blocking_hours | gate_share_of_blocking |
| --- | --- | --- | --- | --- | --- | --- |
| compact800 | ABC | 8 | 12.00 | 8.69 | 3.31 | 0.72 |
| compact800 | ABC | 20 | 76.14 | 58.30 | 17.83 | 0.77 |
| compact800 | Spread | 8 | 7.70 | 6.54 | 1.16 | 0.85 |
| compact800 | Spread | 20 | 57.18 | 50.01 | 7.17 | 0.87 |
| coverage90 | ABC | 8 | 0.68 | 0.27 | 0.41 | 0.40 |
| coverage90 | ABC | 20 | 4.71 | 2.06 | 2.65 | 0.44 |
| coverage90 | Spread | 8 | 0.29 | 0.26 | 0.03 | 0.90 |
| coverage90 | Spread | 20 | 1.96 | 1.70 | 0.26 | 0.87 |

## Larger-layout density extension

The larger layout has 115 aisles; comparing only 1-20 total pickers would test a much lower density than the compact layout. These additional runs use three-order S-shape tours and the same modeled traffic control. Paired intervals here are pointwise, not a new pre-specified simultaneous crossover test.

| pickers | pickers_per_10_aisles | spread_minus_abc | ci_low | ci_high |
| --- | --- | --- | --- | --- |
| 23 | 2.00 | -19.95 | -21.20 | -18.70 |
| 46 | 4.00 | -32.92 | -34.97 | -30.88 |
| 69 | 6.00 | -36.41 | -38.67 | -34.16 |
| 92 | 8.00 | -27.30 | -31.98 | -22.62 |
| 138 | 12.00 | 44.70 | 34.03 | 55.37 |
| 184 | 16.00 | 72.86 | 56.69 | 89.03 |
| 230 | 20.00 | 82.88 | 66.70 | 99.05 |

## Validation

```json
{
  "main_replications": 2160,
  "supplemental_replications": 740,
  "experiment_cells": 290,
  "replications_per_cell": 10,
  "one_picker_verification_cases": 320,
  "max_relative_verification_error": 9.347172302070875e-15,
  "stream_recycled": false,
  "time_conservation": true,
  "order_flow_conservation": true,
  "single_picker_blocking_zero": true,
  "passing_blocking_zero": true
}
```

See tests/, verification.csv, data_integrity.json, and METHODS.md. The results are exploratory design evidence. Collect actual geometry, batch/cart limits, entry rules, passing observations, service times, tail-order handling and demand before a production decision. The optional Simio rebuild, middle cross aisle, re-slotting and seed-savings batching were not required for the three completed stages and are not claimed as implemented.
