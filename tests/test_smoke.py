import importlib

MODULES = [
    "trading",
    "trading.config",
    "trading.data",
    "trading.features",
    "trading.labels",
    "trading.validation",
    "trading.models",
    "trading.calibration",
    "trading.signals",
    "trading.backtest",
    "trading.metrics",
    "trading.viz",
]


def test_all_modules_import():
    for name in MODULES:
        importlib.import_module(name)
