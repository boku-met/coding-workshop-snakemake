# Independent exercise: build, observe, then generalize

## Goal

Extend the starter `Snakefile` until it can first produce the conventional
30 °C heat-day figure:

```text
figures/heat_days_ge_30.png
```

Then generalize the working rules so that the same workflow also produces the
25 and 35 °C figures. The Python scripts are already provided; your task is to
declare their file contracts.

## Checkpoint 1 — Count heat days at 30 °C

The starter already prepares the raw observations. Add a `count_heat_days`
rule with this contract:

| Role | Value |
|---|---|
| Input | `data/processed/vienna_hohe_warte_tlmax.csv` |
| Output | `results/heat_days_ge_30.csv` |
| Parameter | `threshold=30` |
| Script | `scripts/count_heat_days.py` |

The script interface is:

```text
python scripts/count_heat_days.py --input INPUT --threshold 30 --output OUTPUT
```

Use the named placeholders `{input.daily}`, `{params.threshold}`, and
`{output.counts}` in the shell command. Then inspect the requested count file:

```bash
snakemake -n -p results/heat_days_ge_30.csv
```

Before continuing, explain which path connects this rule to
`prepare_temperature_data` and which concrete values replace the placeholders.

<details>
<summary>Syntax hint</summary>

```python
rule count_heat_days:
    input:
        daily="data/processed/vienna_hohe_warte_tlmax.csv"
    output:
        counts="results/heat_days_ge_30.csv"
    params:
        threshold=30
    shell:
        """
        python scripts/count_heat_days.py \
          --input {input.daily} \
          --threshold {params.threshold} \
          --output {output.counts}
        """
```

</details>

## Checkpoint 2 — Produce the 30 °C figure

Add a `plot_heat_days` rule that connects the count file to:

```text
figures/heat_days_ge_30.png
```

Its script interface is:

```text
python scripts/plot_heat_days.py --input INPUT --output OUTPUT
```

Predict the jobs in this dry-run, then execute the target:

```bash
snakemake -n -p figures/heat_days_ge_30.png
snakemake -j 1 figures/heat_days_ge_30.png
```

Open the figure. Hollow points mark years with incomplete coverage; the final
red point is provisional and annotated with the latest usable observation.

<details>
<summary>Syntax hint</summary>

```python
rule plot_heat_days:
    input:
        counts="results/heat_days_ge_30.csv"
    output:
        figure="figures/heat_days_ge_30.png"
    shell:
        """
        python scripts/plot_heat_days.py \
          --input {input.counts} \
          --output {output.figure}
        """
```

</details>

## Checkpoint 3 — Observe workflow state

Request the same target again:

```bash
snakemake -j 1 figures/heat_days_ge_30.png
```

It should report that there is nothing to do. Now remove the two downstream
outputs and predict the dry-run before reading it:

```bash
rm results/heat_days_ge_30.csv figures/heat_days_ge_30.png
snakemake -n -p figures/heat_days_ge_30.png
```

Why are `count_heat_days` and `plot_heat_days` scheduled, while
`prepare_temperature_data` is not? Run the target once more to restore the
complete 30 °C chain. Notice that removing only an intermediate file would not
trigger work while the requested final figure itself remains current.

## Checkpoint 4 — Generalize the working rules

The three thresholds would otherwise require repeated rules. Replace the
literal `30` in the count and figure paths with the wildcard `{threshold}`.
Also replace the fixed parameter with:

```python
params:
    threshold="{threshold}"
```

A request for `figures/heat_days_ge_25.png` can now bind the wildcard to `25`
and create one concrete job from each rule pattern.

Finally, add an aggregate target for all desired figures:

```python
THRESHOLDS = [25, 30, 35]

rule all:
    input:
        expand("figures/heat_days_ge_{threshold}.png", threshold=THRESHOLDS)
    default_target: True
```

`expand()` creates a concrete list of filenames. The producing rules retain
wildcard patterns. Inspect and execute the default target:

```bash
snakemake -n -p
snakemake -j 1
```

You should finish with three count files and three figures. If you remain
blocked after using the hints, compare your work with `solutions/Snakefile`.
