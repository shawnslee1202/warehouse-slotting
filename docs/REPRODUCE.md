# Reproduction

Requires Python 3.12 and about 2 GB of free disk space for raw and intermediate data. Four worker processes are used by default. The output package includes measured results, so installing Python or downloading the data is unnecessary for reading the report, charts, dashboard or notebooks.

Run from the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m warehouse_slotting.data.download --out data/raw
python -m warehouse_slotting.data.prepare --raw data/raw --out data/processed
python -m warehouse_slotting.validation.audit --root . --raw data/raw
python -m unittest discover -s tests -v
python -m warehouse_slotting.experiment.run build --processed data/processed --cache cache --results results
python -m warehouse_slotting.experiment.run run --cache cache --results results --workers 4 --reps 10
python -m warehouse_slotting.experiment.supplement --cache cache --results results
python -m warehouse_slotting.analysis.analyze --root .
python -m warehouse_slotting.validation.audit --root .
python -m warehouse_slotting.reporting.deliver --root .
```

Use a fresh results directory for a clean rerun. The main experiment runner resumes complete groups from replications.csv; do not mix different seeds, geometries or code versions in one results directory. The supplemental runner refuses to overwrite its existing replication CSV. To preserve delivered evidence, copy the repository and move its results directory aside before a full reproduction. Downloading verifies pinned SHA-256 values; if the mirror disappears, obtain the five original CSVs from an authorized source and supply their directory to prepare.

The exact outputs in this package used Python 3.12, NumPy 2.5.4, pandas 3.0.1, SciPy 1.18.1, SimPy 4.1.2, Matplotlib 3.11.2 and ReportLab 4.4.9. Computational run times depend on hardware. No Simio license or paid service is required. Network access is only needed for libraries and initial data download.

The two notebooks are saved with executed outputs. They inspect delivered CSVs rather than re-running the expensive simulation. They can be opened in any Jupyter-compatible viewer; install JupyterLab separately if needed. dashboard.html works offline after extraction; it neither uploads data nor needs a server.

The delivered verification includes tests of hand-calculated routes, pick conservation, frozen-last ordering, no-interference controls, opposing-traffic liveness, time/flow accounting and exact agreement between event-cell and reservation-based SimPy implementations. verification.csv also records direct one-picker checks on 320 held-out order/policy/routing combinations.
