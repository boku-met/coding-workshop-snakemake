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

Use the `shell` directive to call this command with its arguments.

Use the named placeholders `{input.daily}`, `{params.threshold}`, and
`{output.counts}` in the shell command. Then inspect the requested count file:

```bash
snakemake -n -p results/heat_days_ge_30.csv
```

Before continuing, explain which path connects this rule to
`prepare_temperature_data` and which concrete values replace the placeholders.

Hint: use the starter rule as a syntax reference.

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

Hint: the plot rule's input must match the count rule's output exactly.
Name the input `counts` and the output `figure`, and use their named
placeholders in the shell command.

## Checkpoint 3 — Observe workflow state

Request the same target again:

```bash
snakemake -j 1 figures/heat_days_ge_30.png
```

It should report that there is nothing to do. Now remove the two downstream
outputs and the planned work:

```bash
rm results/heat_days_ge_30.csv figures/heat_days_ge_30.png
snakemake -n -p figures/heat_days_ge_30.png
```

`count_heat_days` and `plot_heat_days` are scheduled because their
outputs are required but missing, while `prepare_temperature_data` is
not. Run the target once more to restore the complete 30 °C chain.
Notice that removing only an intermediate file would not trigger work
while the requested final figure itself remains current.

Now change one temperature value in the processed CSV and save it. Keep the
bundled raw observations unchanged.

Before running anything, predict which rules need to rerun:

```bash
snakemake -n -p figures/heat_days_ge_30.png
```

Why are `count_heat_days` and `plot_heat_days` scheduled, while
`prepare_temperature_data` is not?

Finally, regenerate the processed data from the original observations, then
rebuild the figure:

```bash
snakemake -j 1 --force data/processed/vienna_hohe_warte_tlmax.csv
snakemake -j 1 figures/heat_days_ge_30.png
```

## Checkpoint 4 — Generalize the working rules

For the workshops sake, let's ignore the conventional definition of
heatdays and experiment with 25 and 35 °C thresholds by generalize the
rules. The three thresholds would otherwise require repeated rules.
Replace the literal `30` in the count and figure paths with the wildcard
`{threshold}`. Also make the `threshold` parameter take its value from
the wildcard instead of a fixed number. Snakemake can substitute
wildcards in parameter strings.

A request for `figures/heat_days_ge_25.png` can now bind the wildcard to `25`
and create one concrete job from each rule pattern.

Finally, define the desired thresholds (25, 30, and 35 °C) and add an aggregate
rule named `all`. Use `expand()` with the figure path pattern and those
thresholds to declare its inputs. Mark this rule as the default target with
the `default_target` directive so that running Snakemake without a filename
requests all three figures.

`expand()` creates a concrete list of filenames. The producing rules retain
wildcard patterns. Inspect and execute the default target:

```bash
snakemake -n -p
snakemake -j 1
```

Hint: If you initially defined the threshold parameter as integer, now
make sure note to forget quotes around the wildcard.

You should finish with three count files and three figures. If you remain
blocked after using the hints, compare your work with the
[complete solution](../solutions/Snakefile).
