"""Module to plots metrics"""
from __future__ import annotations
from typing import Any
from pathlib import Path
import csv
from overrides import overrides
import pytorch_lightning as pl
from pytorch_lightning.utilities.rank_zero import rank_zero_only
from pytorch_lightning.loggers import CSVLogger
import matplotlib.pyplot as plt
import numpy as np

from ..logger import lme_logger as logger

def _norm(x: list[float]) -> np.ndarray:
    x = np.array(x)
    median = np.nan_to_num(np.nanmedian(x), nan=0)
    x: np.ndarray = np.nan_to_num(x, nan=median)
    return x.clip(-2 * np.sign(median) * median, 2 * np.sign(median) * median)

def _float_or_nan(x: str) -> float:
    try:
        return float(x)
    except ValueError:
        return float("nan")

class PlotMetrics(pl.Callback):
    """Plot metrics implementation"""
    def __init__(self):
        self.log_dir = None

    def _plot_best_dot(self, ax: plt.Axes, scores: list[float], higher_is_better: bool):
        """Plot the dot. We require to know if the metric is max or min typed."""
        scores = np.nan_to_num(scores, nan=-10**5 if higher_is_better else 10**5)
        metric_x = np.argmax(scores) if higher_is_better else np.argmin(scores)
        metric_y, norm_metric_y = scores[metric_x], _norm(scores)[metric_x]
        ax.annotate(f"Epoch {metric_x + 1}\nBest {metric_y:.2f}", xy=(metric_x + 1, norm_metric_y))
        ax.plot([metric_x + 1], [norm_metric_y], "o")

    def _do_plot(self, csv_data: list[dict[str, float]], metric_name: str, higher_is_better: bool, out_file: str):
        """Plot the figure with the metric"""
        ax = (fig := plt.figure()).gca()
        x_plot = range(1, len(csv_data) + 1)
        train_y = [row[metric_name] for row in csv_data]
        val_y = [row[f"val_{metric_name}"] for row in csv_data] if f"val_{metric_name}" in csv_data[0].keys() else None
        ax.plot(x_plot, _norm(train_y), label="train")
        if val_y is not None:
            ax.plot(x_plot, _norm(val_y), label="validation")
        self._plot_best_dot(ax, train_y if val_y is None else val_y, higher_is_better)
        ax.set_xlabel("Epoch")
        name_trimmed = metric_name if len(metric_name) < 35 else f"{metric_name[0: 25]}...{metric_name[-7:]}"
        ax.set_title(f"{name_trimmed}({'↑' if higher_is_better else '↓'})")
        fig.legend()
        fig.savefig(out_file)
        plt.close(fig)

    @rank_zero_only
    @overrides
    def on_fit_start(self, trainer: pl.Trainer, pl_module: pl.LightningModule) -> None:
        assert any(isinstance(logger, CSVLogger) for logger in trainer.loggers), trainer.loggers
        self.log_dir = trainer.loggers[0].log_dir

    @rank_zero_only
    @overrides
    # pylint: disable=consider-using-with
    def on_train_epoch_start(self, trainer: pl.Trainer, pl_module: Any):
        if not Path(pth := f"{self.log_dir}/metrics.csv").exists():
            logger.debug(f"No metrics.csv found in log dir: '{self.log_dir}'. Skipping this epoch")
            return
        csv_data = [{k: _float_or_nan(v) for k, v in row.items()}
                    for row in csv.DictReader(open(pth, encoding="utf-8")) if row["epoch"] != ""]
        found_metrics = [x for x in csv_data[0].keys() if x in {"loss", *pl_module.metrics.keys()}]
        for metric_name in found_metrics:
            higher_is_better = pl_module.metrics[metric_name].higher_is_better if metric_name != "loss" else False
            self._do_plot(csv_data, metric_name, higher_is_better, out_file=f"{self.log_dir}/{metric_name}.png")
