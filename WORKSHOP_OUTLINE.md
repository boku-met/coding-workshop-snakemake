# Workshop outline: Snakemake through Vienna heat days

## Goal

The workshop develops the ability to read and extend a small Snakemake
workflow built from file-producing rules. The first result is the annual
30 °C heat-day figure for Wien Hohe Warte; the completed workflow generalizes
the same rules to three thresholds.

## Learning outcomes

The session covers:

1. identifying the input, action, and output of a rule;
2. requesting a concrete file target and reading a dry-run;
3. explaining how matching file paths connect rules into a DAG;
4. using `{input}`, `{output}`, and `{params...}` placeholders;
5. using a wildcarded output pattern and `expand()` to request repeated outputs;
6. predicting which rules rerun after an upstream file changes.

## 90-minute schedule

| Time | Format | Content |
|---:|---|---|
| 0:00–0:05 | Input | Manual commands and the coordination they leave implicit |
| 0:05–0:12 | Input | Rule contracts, placeholders, and concrete targets |
| 0:12–0:20 | Input | Inferred DAG, target rules, wildcards, and `expand()` |
| 0:20–0:25 | Demo/handoff | Dry-run, execute, observe no-op, and introduce the checkpoints |
| 0:25–1:10 | Independent work | Build the fixed 30 °C chain, observe it, then generalize it |
| 1:10–1:25 | Wrap-up | Group recap of DAG and rerun behaviour |
| 1:25–1:30 | Outlook | Reprotrail as a possible future result-centred layer |

Environment creation and validation are required before this schedule begins.

## Required path

```text
data/raw/vienna_hohe_warte_tlmax.csv
        ↓ prepare_temperature_data
data/processed/vienna_hohe_warte_tlmax.csv
        ↓ count_heat_days
results/heat_days_ge_30.csv
        ↓ plot_heat_days
figures/heat_days_ge_30.png
```

After this concrete chain works, `{threshold}` turns both output paths into
rule patterns and `expand()` defines the 25, 30, and 35 °C aggregate target.
No-op and partial-rerun behaviour are observed before that generalization.
