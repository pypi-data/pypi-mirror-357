from ..utils._parameter_validation import Interval
from ._transductive_estimator import TransductiveEstimator
from ..algorithms.src.tdbscan.binaries.tdbscan_core import tdbscan_main
from ..algorithms.src.tdbscan.binaries.tdbscan_postprocess import tdbscan_postprocess

import numpy as np

class TDBSCAN(TransductiveEstimator):
    _parameter_constraints: dict = {
        "eps": Interval(float, 0, 1e32, closed="neither"),
        "k": Interval(int, 1, 1e32, closed="left")
    }
    def __init__(self, eps: float, k: int, metric="minkowski", p=2, new_clusters=True):
        super().__init__(eps=eps, k=k)
        self.eps = eps
        self.k = k
        self.new_clusters = new_clusters
        self.metric = metric
        self.p = p
    def fit(self, X, y, threshold=-1):
        super().fit(X, y)
        self.labels_ = tdbscan_main(self._algorithm_input.data, self.eps, self.k, self.y_.astype(np.int32), self.metric, self.p)
        if not self.new_clusters:
            self.labels_ = tdbscan_postprocess(self._algorithm_input.data, self.labels_, self.metric, self.p, threshold)
        self.is_fitted = True  

    def fit_predict(self, X, y):
        super().fit_predict(X, y)
        self.is_fitted = True
        return self.labels_