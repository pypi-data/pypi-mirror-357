"""Multi class F1 Score"""
from __future__ import annotations
from overrides import overrides
import torch as tr
from torchmetrics.functional.classification import multiclass_stat_scores

from .core_metric import CoreMetric


class MultiClassF1Score(CoreMetric):
    """Multi class F1 Score implementation"""

    def __init__(self, num_classes: int):
        super().__init__(higher_is_better=True)
        self.num_classes = num_classes
        self.batch_results = tr.zeros(4, num_classes).type(tr.DoubleTensor)

    @overrides
    def forward(self, y: tr.Tensor, gt: tr.Tensor) -> tr.Tensor:
        assert y.dtype in (tr.int64, tr.float32) and gt.dtype in (tr.int64, tr.float32), (y.dtype, gt.dtype)
        # support for both index tensors as well as float gt tensors (if one_hot in dataset)
        gt_argmax = gt.argmax(-1) if gt.dtype == tr.float else gt
        y_argmax = y.argmax(-1) if y.dtype == tr.float else y
        stats = multiclass_stat_scores(y_argmax, gt_argmax, num_classes=self.num_classes, average=None)
        return stats[:, 0:4].T # TP, FP, TN, FN

    @overrides
    def batch_update(self, batch_result: tr.Tensor) -> None:
        self.batch_results = self.batch_results.to(batch_result.device) + batch_result.detach()

    @overrides
    def epoch_result(self) -> tr.Tensor | None:
        tp, fp, _, fn = self.batch_results
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * precision * recall / (precision + recall)
        f1[tr.isnan(f1)] = 0
        return f1

    @overrides
    def epoch_result_reduced(self, epoch_result: tr.Tensor | None) -> tr.Tensor | None:
        """One f1 score per class => average of all f1 scores"""
        return epoch_result.mean()

    @overrides
    def reset(self):
        self.batch_results *= 0

    def __str__(self):
        return f"MultiClassF1Score ({self.num_classes} classes)"
