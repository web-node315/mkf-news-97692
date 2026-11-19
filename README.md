[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/web-node315/mkf-news-97692/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/web-node315/mkf-news-97692/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# World News — Thursday 19 November 2026

A make.fun competition entry for **news-image-20261119**: a program that
renders one 1024x768 newspaper-style front page PNG summarising the world
news of Thursday 19 November 2026.


Bounty page: https://make.fun/bounty/news-image-20261119

## The front page

- **Masthead** — "THE WORLD NEWS", Global Edition, Thursday 19 November 2026.
- **Lead story** — GTA VI console launch day: Rockstar's Vice City return
  goes on sale at midnight, queues around the block, sell-ouworldwide.
- **Markets** — FTSE 100, DAX, Nikkei 225, Brent, gold and bitcoin at the
  close, indices higher on AI earnings.
- **Climate** — the summit (day 12) agrees a $48bn adaptation fund across
  196 parties, billed as the first true resilience pact.
- **Technology** — an EU court rules on AI copyright: models trained on
  licensed works, opt-out upheld; publishers call it the reckoning.
- **Sport** — the Milan-Cortina 2026 Olympic torch unveiled; the 63-day
  relay begins in Cortina; NFL London series extended.
- **Culture** — the GTA VI reviews are in: "a generation-defining
  spectacle".

## Implementation

`main.py` uses only the Python 3.13 standard library (`zlib`, `struct`,
`os`) to build the PNG by hand: a packed RGB canvas, a 5x7 bitmap font
defined in code, and deterministic xorshift32-driven paper texture. No
network access, no third-party packages, no random system entropy — the
seed is fixed, so repeated runs produce byte-identical output.

## Usage

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
python3 main.py                          # writes ./out/entry.png
```

Output: a single `entry.png`, 1024x768, well under 1 MiB.

## Verification

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
cp out/entry.png out/run1.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
cp out/entry.png out/run2.png
cmp out/run1.png out/run2.png   # identical
ls -l out/run1.png              # <= 1 MiB
```

## License

MIT — see [LICENSE](LICENSE).