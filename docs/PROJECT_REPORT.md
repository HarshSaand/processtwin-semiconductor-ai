# ProcessTwin

Project report | Harsh Saand | 22 September 2026

## The problem

Oxidation and diffusion settings affect film thickness and dopant profiles. ProcessTwin gives a user a way to explore these relationships and test candidate settings against an explicit analytical simulator.

## What a user gets

Supply process settings to obtain profiles and scalar predictions, or specify a target and examine inverse-designed recipes checked by the same simulator. Outputs include profiles, candidate settings and evaluation records.

## Practical value

The usable result is an inspectable process-modelling workflow. Reported errors establish agreement with generated analytical targets, not measured wafer outcomes. Inverse-design verification shares the simulator assumptions and is not independent experimental validation.

## Logic and flow

```mermaid
flowchart TD
  N0["Temperature/time/process controls"]
  N1["Analytical oxidation + diffusion simulation"]
  N2["Residual MLP + PCA profile reconstruction"]
  N3["Predict or inverse-search -> simulator check"]
  N4["Profiles + recipes + uncertainty diagnostics"]
  N0 --> N1
  N1 --> N2
  N2 --> N3
  N3 --> N4
```

<details>
<summary><strong>Dataset at a glance</strong></summary>

The saved [`data/simulated.npz`](https://github.com/HarshSaand/processtwin-semiconductor-ai/blob/25f8f69d905d167021c0d4bf34efbda7a4173046/data/simulated.npz) contains **6,000 synthetic process recipes**, generated locally by the reduced-order oxidation/diffusion simulator; not measurements from a fab. One example combines process settings (temperatures, times, wet/dry ambient, dopant species, dose and implantation/background parameters) with simulated oxide thickness, junction depth, peak concentration and a **121-point concentration-versus-depth profile**. The file stores recipe/target records, log-concentration profiles and their shared depth grid.

| Partition | Recipes | Purpose |
|---|---:|---|
| Training | 4,105 | Fit the surrogate |
| Validation | 458 | Model selection |
| Test | 477 | Held-out temperature-bin evaluation |
| High-temperature OOD | 960 | Check behaviour outside the training anneal-temperature range |

Validation/test assignments hold out complete 25°C anneal-temperature bins; OOD recipes use annealing temperatures of 1,055-1,150°C. These counts describe the saved run, not independent physical wafers. See [`src/processtwin/data.py`](https://github.com/HarshSaand/processtwin-semiconductor-ai/blob/25f8f69d905d167021c0d4bf34efbda7a4173046/src/processtwin/data.py) for generation and splitting.

</details>

<details>
<summary><strong>Technical snapshot</strong></summary>

| Question | Implementation |
|---|---|
| What is being approximated? | A declared reduced-order simulator for silicon oxidation and 1D dopant diffusion |
| What does the model predict? | Oxide thickness, junction depth, peak concentration, and the full depth profile |
| How is the profile represented? | PCA coefficients reconstructed into a concentration profile |
| How is model disagreement exposed? | An uncalibrated dispersion band from three residual MLP members plus an OOD warning |
| How is inverse design checked? | Candidate recipes are rerun through the physics simulator before being reported |

### Held-out simulator-fidelity result

| Target | Interpolation R² |
|---|---:|
| Oxide thickness | 0.9968 |
| Junction depth | 0.9985 |

These values measure fidelity to the declared simulator on the saved held-out split. They are not evidence of accuracy against fabricated wafers.

The complete saved evaluation is in [`outputs/metrics.json`](https://github.com/HarshSaand/processtwin-semiconductor-ai/blob/25f8f69d905d167021c0d4bf34efbda7a4173046/outputs/metrics.json). Two results are especially important for interpretation:

- The surrogate took 17.17 μs/recipe versus 11.32 μs/recipe for the simple physics solver on the interpolation test (0.66× measured speedup), so this experiment does **not** establish general acceleration over the reduced-order simulator. On the saved OOD set, the measured ratio was 3.40×.
- The nominal 90% three-member ensemble bands covered 79.9% of oxide, 77.8% of junction, and 86.2% of peak targets on the test split, with lower coverage on OOD data. They are therefore reported as uncalibrated model-disagreement bands, not calibrated predictive intervals.

</details>

<details>
<summary><strong>Implemented</strong></summary>

- Deal-Grove thermal oxidation with temperature-dependent coefficients
- Arrhenius boron/phosphorus diffusivity and dose-conserving 1D Gaussian broadening
- Deterministic 6,000-recipe simulated DOE with blocked interpolation and high-temperature OOD sets
- Polynomial ridge/PCA baseline and three-member residual MLP/PCA ensemble
- Oxide, junction, peak-concentration and full-profile metrics
- Ensemble disagreement bands, OOD warning, and simulator-verified inverse recipe design
- Streamlit process explorer, tests, saved artifacts, DOCX/PDF report

</details>

<details>
<summary><strong>Outputs</strong></summary>

- `data/simulated.npz`: recipes, profiles, split labels and depth grid
- `artifacts/surrogate.joblib`: baseline, PCA and three MLP ensemble members
- `outputs/metrics.json`: measured interpolation and OOD results
- `outputs/inverse_design.json`: simulator-verified inverse design example
- `outputs/processtwin_report.docx` and `.pdf`: presentation-ready technical report

</details>

<details>
<summary><strong>Scientific scope</strong></summary>

Ground truth is generated locally from simplified continuum models and literature-scale coefficients. The simulator omits geometry effects, segregation, clustering, transient-enhanced diffusion, implant damage, stress, equipment variation, and fab calibration. Quantitative results establish surrogate fidelity to this declared simulator only.

The inverse-design example is verified against the same simplified solver that generated the training targets. It demonstrates numerical search and simulator consistency; it does not establish physical recipe validity, uniqueness, manufacturability, or transfer to a fabrication process.

</details>

<details>
<summary><strong>Using the project</strong></summary>

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

</details>

## Evidence and reproduction references

Source revision: 25f8f69d905d167021c0d4bf34efbda7a4173046

- [README.md](https://github.com/HarshSaand/processtwin-semiconductor-ai/blob/25f8f69d905d167021c0d4bf34efbda7a4173046/README.md)
- [docs/output-example.json](https://github.com/HarshSaand/processtwin-semiconductor-ai/blob/25f8f69d905d167021c0d4bf34efbda7a4173046/docs/output-example.json)
- [outputs/metrics.json](https://github.com/HarshSaand/processtwin-semiconductor-ai/blob/25f8f69d905d167021c0d4bf34efbda7a4173046/outputs/metrics.json)

This report describes the source and saved evidence at the revision above. Training and full benchmark runs were not repeated for this documentation release. Dataset, model and dependency licences remain separate from the project documentation.
