# ProcessTwin — Physics-Grounded AI for Silicon Thermal Processing

ProcessTwin combines transparent reduced-order process physics with an AI surrogate for silicon oxidation and dopant diffusion. It predicts oxide thickness, full concentration profiles, junction depth, and uncertainty from a process recipe, and verifies inverse-designed recipes in the physics simulator.

This is an educational research prototype, not commercial TCAD or fab-calibrated process prediction.

## Implemented

- Deal-Grove thermal oxidation with temperature-dependent coefficients
- Arrhenius boron/phosphorus diffusivity and dose-conserving 1D Gaussian broadening
- Deterministic 6,000-recipe simulated DOE with blocked interpolation and high-temperature OOD sets
- Polynomial ridge/PCA baseline and three-member residual MLP/PCA ensemble
- Oxide, junction, peak-concentration and full-profile metrics
- Ensemble uncertainty, OOD warning, and simulator-verified inverse recipe design
- Streamlit process explorer, tests, saved artifacts, DOCX/PDF report

## Quick start — macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/generate_data.py --samples 6000
python scripts/train.py
python scripts/evaluate.py
python scripts/inverse_design.py
streamlit run app.py
```

## Quick start — Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/generate_data.py --samples 6000
python scripts/train.py
python scripts/evaluate.py
python scripts/inverse_design.py
streamlit run app.py
```

## Outputs

- `data/simulated.npz`: recipes, profiles, split labels and depth grid
- `artifacts/surrogate.joblib`: baseline, PCA and three MLP ensemble members
- `outputs/metrics.json`: measured interpolation and OOD results
- `outputs/inverse_design.json`: simulator-verified inverse design example
- `outputs/processtwin_report.docx` and `.pdf`: presentation-ready technical report

## Scientific scope

Ground truth is generated locally from simplified continuum models and literature-scale coefficients. The simulator omits geometry effects, segregation, clustering, transient-enhanced diffusion, implant damage, stress, equipment variation, and fab calibration. Quantitative results establish surrogate fidelity to this declared simulator only.

## Tests

```bash
python -m pytest -q
```

Code and documentation are MIT licensed. Literature coefficients remain attributed to their original sources; see the report.
