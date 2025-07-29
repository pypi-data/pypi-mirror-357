from ..utils._parameter_validation import Interval
from ._transductive_estimator import GraphBasedTransductiveEstimator
from ..algorithms.src.mstl.binaries.mstl_core import clusterize
from ..algorithms.src.genieclust.genieclustering_mst import genieclust_mst
import copy
import numpy as np

class MSTL(GraphBasedTransductiveEstimator):
    _parameter_constraints: dict = {}
    transitional_graphs_types = ("mst")
    def __init__(self):
        super().__init__()
        self.transitional_graphs_ = {k: None for k in MSTL.transitional_graphs_types}

    def fit(self, X, y):
        super().fit(X, y)
        self.generate_graph()

        self.is_fitted = True
    def fit_predict(self, X, y):
        super().fit_predict(X, y)
        return self.labels_
    def _construct_graph(self):
        connections_sparse, weights_sparse = genieclust_mst(self._algorithm_input.data)
        self.transitional_graphs_["mst"] = {"connections": connections_sparse.to_numpy_all(),
                                            "weights": weights_sparse.to_numpy_all()}
        self.graph_connections_, self.graph_weights_, self.labels_ = clusterize(connections_sparse, 
                                                                                weights_sparse,
                                                                                self.y_.astype(np.int8))