# coding workshop: Snakemake

This repository supports a 90-minute introduction to Snakemake. A small
workflow turns daily temperature observations into annual heat-day
figures:

```text
GeoSphere CSV -> cleaned daily data -> annual heat-day counts -> figure
```

A heat day is a calendar day with a maximum temperature of at least 30
°C. The workshop data come from GeoSphere Austria station 5904 at Wien
Hohe Warte.

## Setup before the workshop

Create the environment before the session:

```bash
mamba env create -f environment.yml
conda activate snakemake-heatdays-workshop
```

To reset it use:

```bash
mamba env update -f environment.yml --prune
```

## Workshop starting point

The root `Snakefile` is the starter. It initially contains only the first rule,
which prepares the bundled observations.

Inspect that rule without running it:

```bash
snakemake -n -p data/processed/vienna_hohe_warte_tlmax.csv
```

Then follow [the workshop exercise](exercises/workshop.md) to build the 30 °C
count-and-plot chain, observe its rerun behaviour, and generalize it to 25,
30, and 35 °C with wildcards and `expand()`. A complete solution is available
in `solutions/Snakefile`.

To inspect or run the solution directly:

```bash
snakemake -s solutions/Snakefile -n -p
snakemake -s solutions/Snakefile -j 1
```

## Repository map

```text
Snakefile                 exercise starter
solutions/Snakefile       complete workflow
scripts/                  prewritten scripts
data/raw/                 observations
exercises/workshop.md     instructions
(slides/                  slides             not yet available)
```

## Data source and coverage

The bundled `klima-v2-1d` CSV uses station `5904` (Wien Hohe Warte) and
parameter `tlmax`. Its usable values begin on 1991-04-01. The first and latest
years have incomplete coverage and are marked in each figure; the latest point
is explicitly provisional. See [the source record](data/raw/SOURCE.md) for the
current cutoff, exact request, snapshot checksum, license, and field
definitions.
