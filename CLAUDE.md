# Algorithmic Trading ML Project

## What this is

A learning project to build an ML-powered trading system from scratch, with a focus on rigorous time-series validation and honest results. Not optimized for making money — optimized for demonstrating depth in time-series ML and end-to-end systems thinking.

## Goals (in priority order)

1. Portfolio piece for startup recruiters — depth, polish, communication
2. Deep understanding of time-series ML and validation

## Scope and budget

- 6 weeks, ~50 hours total (~10h/week)
- One asset (SPY), daily bars, ~10 years of history
- One model (XGBoost) + one baseline (logistic regression)
- One advanced technique (purged + embargoed walk-forward CV)
- One depth piece (probability calibration analysis)
- SHAP analysis only if time allows in Week 6

## Locked-in decisions

- **Asset:** SPY (S&P 500 ETF), daily bars, 10+ years from yfinance
- **Prediction target:** binary — does next-day return exceed +0.3%?
- **Strategy direction:** long-only (long when confident, cash otherwise)
- **Costs:** 5 bps commission + 1 bp slippage on entry and exit
- **Validation:** purged + embargoed walk-forward CV (López de Prado)
- **Models:** XGBoost as primary, logistic regression as baseline
- **Calibration:** reliability diagram + Brier score; Platt or isotonic if miscalibrated
- **Honest results commitment:** report what we find, no cherry-picking periods or hyperparameters

## Module structure

Eleven modules, data flows left to right, no backwards imports:

```
config → data → features → models → calibration → signals → backtest → metrics → viz
              ↘ labels ──↗
                  ↑
           validation (uses features, labels, models)
```

| Module | Responsibility |
|---|---|
| `config/` | YAML configs, single source of truth |
| `data/` | Download + cache SPY, validate OHLC |
| `features/` | Technical indicators, derived features |
| `labels/` | Binary target + purge metadata |
| `validation/` | Purged + embargoed walk-forward CV |
| `models/` | XGBoost + baseline behind common interface |
| `calibration/` | Reliability diagrams, Brier, calibrators |
| `signals/` | Probabilities → trading positions |
| `backtest/` | Backtrader integration with realistic costs |
| `metrics/` | Sharpe, drawdown, hit rate, turnover |
| `viz/` | All plotting |

Plus `scripts/` (entry points), `notebooks/` (exploration only), `tests/` (mirrors modules).

No `utils/` module — if something is shared, it gets a real name and its own home.

## Coding standards

- Python 3.11+, managed with `uv`
- Linting and formatting with `ruff`
- Tests with `pytest`, run via `pre-commit` hook
- Type hints on all public functions
- Docstrings on all modules and public functions (Google style)
- Configs in YAML, never hardcoded constants
- Reproducibility: every result comes from `python scripts/<name>.py --config configs/<name>.yaml`

## Testing standards

- Every module has tests in `tests/test_<module>.py`
- Two non-negotiable tests:
  1. **Lookahead test in `features/`:** feed in data with future values NaN'd, confirm features still compute correctly
  2. **Adversarial test in `validation/`:** deliberately construct a leaky model, confirm walk-forward CV reports much worse performance than naive CV
- Target >70% coverage overall; `validation/` and `features/` should be near 100%

## Critical things to never do

- **Never let target leak into features.** Features and labels live in separate modules for a reason.
- **Never use future data in feature calculation.** Every feature at time t uses only data at time ≤ t.
- **Never tune hyperparameters on the test set.** Use train → validate within the walk-forward loop, test only at the end.
- **Never report a Sharpe without confidence intervals or comparison to baselines.**
- **Never delete an honest result and keep retrying until something looks good.** The whole point is rigor.

## Working with Claude Code: Learn vs Build mode

Before each session, decide which mode you're in. This is the project's most important discipline.

**Learn mode** — for high-leverage understanding work. Applies to: `validation/`, `features/`, `calibration/`, the writeup.

1. Read before writing — ask Claude Code to explain the concept first, no code
2. Write the first version yourself, then ask for review
3. Whiteboard test — close the editor and re-derive the logic; if you can't, you don't understand it yet

**Build mode** — for plumbing. Applies to: `config/`, scaffolding, `viz/`, tests, CI, glue code. Let Claude Code rip, review the diffs, move on.

**Hard rule:** never let Claude Code modify `validation/` autonomously. Pair on it actively.

## Success criteria

**Technical:**
- Backtest beats both buy-and-hold and MA crossover after costs (or honest writeup of why it doesn't)
- Walk-forward results reported with confidence intervals
- Model calibration explicitly measured and addressed

**Code quality:**
- All tests pass, CI green
- Reproducible from a single command per workflow
- README readable as a short paper: question, approach, result, what I learned, what's next

**Resume signal:**
- 50+ commits showing steady progress
- README explains decisions and tradeoffs in prose
- One striking visual artifact at the top of the README
