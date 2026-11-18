# Frequent Actor Groups in the IMDb Top 1000 Movies

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/TheRealMamoot/amd-market-basket-imdb/blob/main/main.ipynb)

Market-basket analysis of the [IMDB Movies Dataset](https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows) for the *Algorithms for Massive Datasets* course: each movie is a basket of its billed stars. The notebook compares exhaustive counting, A-Priori (basic and optimized) and PCY, and studies how they scale.

## Running

- **Colab:** open the badge above, add a `KAGGLE_API_TOKEN` secret, and run all cells.
- **Locally:** `pip install -r requirements-dev.txt`, set `KAGGLE_API_TOKEN` in `.env` (see `.env.example`), and run `main.ipynb`.

## Command line

`main.py` runs the same code from the terminal (`python main.py --help` lists all options):

```bash
python main.py --algorithm pcy --min-support 3   # mine once and print the most frequent groups
python main.py --experiment                       # compare all algorithms, saved to results/
python main.py --scaling --augmentation relabeled --variants apriori_optimized pcy  # scalability, saved to results/
```

## Report

The report is [`report.pdf`](report.pdf); its LaTeX source, data and figures are in `report/`. To rebuild it with [Tectonic](https://tectonic-typesetting.github.io):

```bash
python report/make_figures.py                                  # redraw the figures from report/data/
tectonic report/main.tex --outdir . && mv main.pdf report.pdf  # compile into the repository root
```
