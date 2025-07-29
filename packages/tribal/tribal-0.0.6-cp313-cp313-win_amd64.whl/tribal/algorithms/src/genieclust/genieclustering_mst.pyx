# distutils: language=c++
# cython: boundscheck=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: wraparound=False
# cython: language_level=3


## We are only exposing some of these functions (at least, officially)
## in the online manual.
## Many of the "private" members' docstrings should be cleaned up
## and formatted so as to conform to the numpydoc guidelines.
## TODO: (volunteers needed) Cheers.



"""
Internal functions and classes
"""

# ############################################################################ #
#                                                                              #
#   Copyleft (C) 2020-2024, Marek Gagolewski <https://www.gagolewski.com>      #
#                                                                              #
#                                                                              #
#   This program is free software: you can redistribute it and/or modify       #
#   it under the terms of the GNU Affero General Public License                #
#   Version 3, 19 November 2007, published by the Free Software Foundation.    #
#   This program is distributed in the hope that it will be useful,            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the               #
#   GNU Affero General Public License Version 3 for more details.              #
#   You should have received a copy of the License along with this program.    #
#   If this is not the case, refer to <https://www.gnu.org/licenses/>.         #
#                                                                              #
# ############################################################################ #


import numpy as np
cimport numpy as np
np.import_array()
import os

cimport libc.math
from libcpp cimport bool
from libcpp.vector cimport vector
from numpy.math cimport INFINITY
from heapq import heappop, heappush
ctypedef np.float64_t DTYPE_t
ctypedef np.float32_t DTYPE32_t
ctypedef np.int64_t ITYPE_t
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy
from libc.stdint cimport int64_t
from libc.stddef cimport size_t
from libcpp.unordered_set cimport unordered_set

ctypedef fused T:
    int
    long
    long long
    Py_ssize_t
    float
    double

ctypedef fused floatT:
    float
    double




from . cimport c_mst



################################################################################
# Minimum Spanning Tree Algorithms:
# (a) Prim-Jarník's for Complete Undirected Graphs,
# (b) Kruskal's for k-NN graphs,
# and auxiliary functions.
################################################################################

cdef void _openmp_set_num_threads():
    c_mst.Comp_set_num_threads(int(os.getenv("OMP_NUM_THREADS", -1)))




# cpdef tuple mst_from_nn_list(list nns,
#         Py_ssize_t k_max=0,
#         bint stop_disconnected=True,
#         bint verbose=False):
#     """
#     Computes a minimum spanning tree of a (<=k)-nearest neighbour graph
#     using Kruskal's algorithm, and orders its edges w.r.t. increasing weights.
#
#     See `mst_from_nn` for more details.
#
#
#     Parameters
#     ----------
#
#     nns : list of length n
#         Each nns[i] should be a pair of c_contiguous ndarrays.
#         An edge {i, nns[i][0][j]} has weight nns[i][1][j].
#         Each nns[i][0] is of type int32 and nns[i][1] of type float32
#         (for compatibility with nmslib).
#     k_max : int
#         If k_max > 0, O(n*k_max) space will be reserved for auxiliary data.
#     stop_disconnected : bool
#         raise an exception if the input graph is not connected
#     verbose: bool
#         whether to print diagnostic messages
#
#     Returns
#     -------
#
#     pair : tuple
#         See `mst_from_nn`.
#     """
#     cdef Py_ssize_t n = len(nns)
#     cdef np.ndarray[int]   nn_i
#     cdef np.ndarray[float] nn_d
#     cdef Py_ssize_t k
#     cdef Py_ssize_t i, j
#     cdef Py_ssize_t i1, i2
#     cdef float d
#
#     cdef vector[ c_mst.CMstTriple[float] ] nns2
#     if k_max > 0:
#         nns2.reserve(n*k_max)
#
#
#     for i in range(n):
#         nn_i = nns[i][0]
#         nn_d = nns[i][1]
#         k = nn_i.shape[0]
#         if nn_d.shape[0] != k:
#             raise ValueError("nns has arrays of different lengths as elements")
#
#         for j in range(k):
#             i1 = i
#             i2 = nn_i[j]
#             d = nn_d[j]
#             if i2 >= 0 and i1 != i2:
#                 nns2.push_back( c_mst.CMstTriple[float](i1, i2, d) )
#
#     cdef np.ndarray[Py_ssize_t,ndim=2] mst_ind  = np.empty((n-1, 2), dtype=np.intp)
#     cdef np.ndarray[float]          mst_dist = np.empty(n-1, dtype=np.float32)
#
#     cdef Py_ssize_t n_edges = c_mst.Cmst_from_nn_list(nns2.data(), nns2.size(), n,
#             &mst_dist[0], &mst_ind[0,0], verbose)
#
#     if stop_disconnected and n_edges < n-1:
#         raise ValueError("graph is disconnected")
#
#     return mst_dist, mst_ind
#




cpdef tuple mst_from_complete(
    floatT[:,::1] X,
    bint verbose=False): # [:,::1]==c_contiguous
    """A Jarník (Prim/Dijkstra)-like algorithm for determining
    a(*) minimum spanning tree (MST) of a complete undirected graph
    with weights given by a symmetric n*n matrix
    or a distance vector of length n*(n-1)/2.

    (*) Note that there might be multiple minimum trees spanning a given graph.


    References
    ----------

    [1] M. Gagolewski, M. Bartoszuk, A. Cena,
    Genie: A new, fast, and outlier-resistant hierarchical clustering algorithm,
    Information Sciences 363 (2016) 8–23.

    [2] V. Jarník, O jistém problému minimálním,
    Práce Moravské Přírodovědecké Společnosti 6 (1930) 57–63.

    [3] C.F. Olson, Parallel algorithms for hierarchical clustering,
    Parallel Comput. 21 (1995) 1313–1325.

    [4] R. Prim, Shortest connection networks and some generalizations,
    Bell Syst. Tech. J. 36 (1957) 1389–1401.


    Parameters
    ----------

    X : c_contiguous ndarray, shape (n*(n-1)/2, 1) or (n,n)
        distance vector or matrix
    verbose: bool
        whether to print diagnostic messages

    Returns
    -------

    pair : tuple
        A pair (mst_dist, mst_ind) defining the n-1 edges of the MST:
          a) the (n-1)-ary array mst_dist is such that
          mst_dist[i] gives the weight of the i-th edge;
          b) mst_ind is a matrix with n-1 rows and 2 columns,
          where {mst[i,0], mst[i,1]} defines the i-th edge of the tree.

        The results are ordered w.r.t. nondecreasing weights.
        (and then the 1st, and the the 2nd index).
        For each i, it holds mst[i,0]<mst[i,1].
    """
    cdef Py_ssize_t d = X.shape[1]
    cdef Py_ssize_t n = X.shape[0]
    if d == 1:
        n = <Py_ssize_t>libc.math.round((libc.math.sqrt(1.0+8.0*n)+1.0)/2.0)
        assert n*(n-1)//2 == X.shape[0]

    cdef np.ndarray[Py_ssize_t,ndim=2] mst_ind  = np.empty((n-1, 2), dtype=np.intp)
    cdef np.ndarray[floatT]         mst_dist = np.empty(n-1,
        dtype=np.float32 if floatT is float else np.float64)

    cdef c_mst.CDistance[floatT]* D = NULL
    if d == 1:
        D = <c_mst.CDistance[floatT]*>new c_mst.CDistancePrecomputedVector[floatT](&X[0,0], n)
    else:
        assert d == n
        D = <c_mst.CDistance[floatT]*>new c_mst.CDistancePrecomputedMatrix[floatT](&X[0,0], n)

    _openmp_set_num_threads()
    c_mst.Cmst_from_complete(D, n, &mst_dist[0], &mst_ind[0,0], verbose)

    if D:  del D

    return mst_dist, mst_ind

cdef enum DataType:
    INT64 = 0
    FLOAT32 = 1

cdef class GraphWrapper:
    cdef:
        void **_data                      # Array of pointers to the data arrays
        int *_sizes                       # Current sizes of the arrays (degrees of vertices)
        bint _lookup                      # If the set is to be made for each connection array for fast lookups
        size_t _count                     # Number of arrays (number of vertices, datapoints)
        DataType _dtype                   # Data type of all arrays (int64 for connections, float32 for weights)
        int _max_size                     # Maximum size of each array (max degree of vertix)
        unordered_set[int64_t] **_int_sets  # For int64 arrays (connections), a hash set per array

    def __cinit__(self, size_t count, DataType dtype, int max_size, bint lookup_opt=False):
        """
        Initialize the structure with a fixed number of arrays.
        All arrays will have the same data type and maximum size.
        Max degree of the vertix is dictated by the max_size, which is k * 3, otherwise algorithm is considered not convergeable.
        """
        cdef size_t i
        self._count = count
        self._dtype = dtype
        self._max_size = max_size
        self._lookup = lookup_opt
        self._data = <void **>malloc(count * sizeof(void *))
        self._sizes = <int *>malloc(count * sizeof(int))

        # Initialize arrays
        for i in range(count):
            self._sizes[i] = 0
            if dtype == DataType.INT64:
                self._data[i] = <void *>malloc(max_size * sizeof(int64_t))
            elif dtype == DataType.FLOAT32:
                self._data[i] = <void *>malloc(max_size * sizeof(DTYPE32_t))
            else:
                raise ValueError("Unsupported data type")

        # Initialize hash sets for int64 arrays
        if dtype == DataType.INT64 and self._lookup:
            self._int_sets = <unordered_set[int64_t] **>malloc(count * sizeof(void *))
            for i in range(count):
                self._int_sets[i] = new unordered_set[int64_t]()
        else:
            self._int_sets = NULL

    cpdef append(self, ITYPE_t index, value):
        """
        Append an element to the array.
        """
        cdef int size
        cdef int updated_size
        cdef void *data
        cdef int64_t *int_data
        cdef DTYPE32_t *double_data
        cdef int64_t int_value
        if not (0 <= index < self._count):
            raise IndexError("Invalid array index")

        if self._sizes[index] >= self._max_size:
            raise OverflowError("Array has reached its maximum size")

        size = self._sizes[index]

        data = self._data[index]

        if size + 1 > self._max_size:
            raise OverflowError("Max vertix degree surpassed!")

        if self._dtype == DataType.INT64:
            int_data = <int64_t *>data
            int_value = <int64_t>value
            int_data[size] = int_value
            if self._lookup:
                self._int_sets[index].insert(int_value)  # Add to hash set for fast lookup
        elif self._dtype == DataType.FLOAT32:
            double_data = <DTYPE32_t *>data
            double_data[size] = <DTYPE32_t>value
        else:
            raise ValueError("Unsupported data type")
        self._sizes[index] += 1

    cpdef tuple pop_max(self):
        """
        Remove and return the maximum value, its list index, and sublist index
        from all sub-arrays. Removes both occurrences of the maximum value.
        """
        cdef list max_indices = []  # List to store all occurrences of the max value
        cdef float max_value_float = -1  # Minimal float64
        cdef int size
        cdef void *data
        cdef float *float_data
        cdef float temp_value_float

        # First pass: Find the maximum value and collect all its indices
        for i in range(self._count):  # Iterate over all lists
            size = self._sizes[i]
            if size == 0:  # Skip empty sublists
                continue

            data = self._data[i]

            if self._dtype == DataType.FLOAT32:
                float_data = <float *> data
                for j in range(size):
                    temp_value_float = float_data[j]
                    if temp_value_float > max_value_float:
                        # Found a new maximum, reset the list of indices
                        max_value_float = temp_value_float
                        max_indices = [(i, j)]
                    elif temp_value_float == max_value_float:
                        # Found another occurrence of the current maximum
                        max_indices.append((i, j))


        if not max_indices:
            raise ValueError("All sub-arrays are empty, cannot pop max")

        # Remove all occurrences of the maximum value
        for i, j in reversed(max_indices):  # Iterate in reverse to avoid shifting issues
            size = self._sizes[i]
            data = self._data[i]
            if self._dtype == DataType.FLOAT32:
                float_data = <float *> data
                # Shift elements left to remove the occurrence
                for k in range(j, size - 1):
                    float_data[k] = float_data[k + 1]
                # if self._lookup:
                #     self._float_sets[i].erase(max_value_float)  # Update lookup
                self._sizes[i] -= 1

        # Return information about the first occurrence
        first_node_index = max_indices[0][0]
        snd_node_index = max_indices[1][0]
        return first_node_index, snd_node_index

    cpdef  pop(self, int list_index, int element_index):
        """
        Remove and return the element at the specified index from a sublist.

        Parameters:
            list_index (int): Index of the list from which to remove the element.
            element_index (int): Index of the element to remove within the sublist.

        Returns:
            int: The removed element.
        """
        cdef int size
        cdef void *data
        cdef int i

        # Validate list_index
        if list_index < 0 or list_index >= self._count:
            raise IndexError("List index out of range")

        # Get the size of the specified sublist
        size = self._sizes[list_index]

        if size == 0:
            raise IndexError("Cannot pop from an empty sublist")

        # Validate element_index
        if element_index < 0 or element_index >= size:
            raise IndexError("Element index out of range")



        data = self._data[list_index]

        if self._dtype == DataType.INT64:
            int_data = <int64_t *>data
            removed_value = int_data[element_index]

            # if self._lookup:
            #     self._int_sets[list_index].remove(removed_value)  # Add to hash set for fast lookup
            for i in range(element_index, size - 1):
                int_data[i] = int_data[i + 1]

        elif self._dtype == DataType.FLOAT32:
            double_data = <DTYPE32_t *>data
            removed_value = double_data[element_index]

            for i in range(element_index, size - 1):
                double_data[i] = double_data[i + 1]

        else:
            raise ValueError("Unsupported data type")

        self._sizes[list_index] -= 1

        return removed_value

    cpdef contains(self, int64_t index, int64_t value):
        """
        Check if a value exists in the array.
        Performable only for `int` arrays for O(1) set performance.
        """
        cdef int64_t target

        if not (0 <= index < self._count):
            raise IndexError("Invalid array index")

        if self._dtype != DataType.INT64:
            raise TypeError("Membership check only supported for int64 arrays")

        target = <int64_t>value
        return self._int_sets[index].count(target) > 0

    cpdef to_numpy(self, ITYPE_t index):
        """
        Convert the specified array to a NumPy array by copying the data from stored arrays.
        """
        cdef int size
        cdef np.ndarray arr
        cdef int64_t *int_data
        cdef DTYPE32_t *double_data

        if not (0 <= index < self._count):
            raise IndexError("Invalid array index")

        size = self._sizes[index]

        if self._dtype == DataType.INT64:
            arr = np.empty(size, dtype=np.int64)
            int_data = <int64_t *>self._data[index]
            memcpy(<void *>arr.data, <void *>int_data, size * sizeof(int64_t))
        elif self._dtype == DataType.FLOAT32:
            arr = np.empty(size, dtype=np.float32)
            double_data = <DTYPE32_t *>self._data[index]
            memcpy(<void *>arr.data, <void *>double_data, size * sizeof(DTYPE32_t))
        else:
            raise ValueError("Unsupported data type")

        return arr

    def to_numpy_all(self):
        """
        Convert all arrays to a list of NumPy arrays.
        """
        cdef int i
        cdef list result = []

        for i in range(self._count):
            result.append(self.to_numpy(i))

        return result

    def __dealloc__(self):
        cdef size_t i

        for i in range(self._count):
            if self._data[i] != NULL:
                free(self._data[i])

        free(self._data)
        free(self._sizes)

        # Deallocate hash sets for int64 arrays
        if self._dtype == DataType.INT64 and self._int_sets != NULL:
            for i in range(self._count):
                if self._int_sets[i] != NULL:
                    del self._int_sets[i]
            free(self._int_sets)

cpdef tuple genieclust_mst(floatT[:,::1] X, str metric="euclidean"):
    cdef int i, n
    max_degree = 0 
    n = len(X)
    cdef np.ndarray[Py_ssize_t] degrees = np.zeros(n, dtype=np.intp)
    
    cdef np.ndarray[Py_ssize_t,ndim=2] mst_ind  = np.empty((n-1, 2), dtype=np.intp)
    cdef np.ndarray[floatT]         mst_dist = np.empty(n-1,
        dtype=np.float32 if floatT is float else np.float64)

    # Genieclust MST
    mst_dist, mst_ind = mst_from_distance(X, metric)


    mst_connections = GraphWrapper(n, DataType.INT64, n)
    mst_weights = GraphWrapper(n, DataType.FLOAT32, n)

    for i in range(n-1):
        # Non-repeating
        mst_connections.append(mst_ind[i][0], mst_ind[i][1])
        mst_connections.append(mst_ind[i][1], mst_ind[i][0])

        mst_weights.append(mst_ind[i][0], mst_dist[i])
        mst_weights.append(mst_ind[i][1], mst_dist[i]) # same weight

    return mst_connections, mst_weights


cpdef tuple mst_from_distance(
    floatT[:,::1] X,
    str metric="euclidean",
    floatT[::1] d_core=None,
    bint verbose=False):
    """A Jarník (Prim/Dijkstra)-like algorithm for determining
    a(*) minimum spanning tree (MST) of X with respect to a given metric
    (distance). Distances are computed on the fly.
    Memory use: O(n).


    References
    ----------

    [1] M. Gagolewski, M. Bartoszuk, A. Cena,
    Genie: A new, fast, and outlier-resistant hierarchical clustering algorithm,
    Information Sciences 363 (2016) 8–23.

    [2] V. Jarník, O jistém problému minimálním,
    Práce Moravské Přírodovědecké Společnosti 6 (1930) 57–63.

    [3] C.F. Olson, Parallel algorithms for hierarchical clustering,
    Parallel Comput. 21 (1995) 1313–1325.

    [4] R. Prim, Shortest connection networks and some generalizations,
    Bell Syst. Tech. J. 36 (1957) 1389–1401.


    Parameters
    ----------

    X : c_contiguous ndarray, shape (n,d) or,
            if metric == "precomputed", (n*(n-1)/2,1) or (n,n)
        n data points in a feature space of dimensionality d
        or pairwise distances between n points
    metric : string
        one of ``"euclidean"`` (a.k.a. ``"l2"``),
        ``"manhattan"`` (synonyms: ``"cityblock"``, ``"l1"``),
        ``"cosine"`` (a.k.a. ``"cosinesimil"``), or ``"precomputed"``.
        More metrics/distances might be supported in future versions.
    d_core : c_contiguous ndarray of length n; optional (default=None)
        core distances for computing the mutual reachability distance
    verbose: bool
        whether to print diagnostic messages

    Returns
    -------

    pair : tuple
        A pair (mst_dist, mst_ind) defining the n-1 edges of the MST:
          a) the (n-1)-ary array mst_dist is such that
          mst_dist[i] gives the weight of the i-th edge;
          b) mst_ind is a matrix with n-1 rows and 2 columns,
          where {mst[i,0], mst[i,1]} defines the i-th edge of the tree.

        The results are ordered w.r.t. nondecreasing weights.
        (and then the 1st, and the the 2nd index).
        For each i, it holds mst[i,0]<mst[i,1].
    """
    cdef Py_ssize_t n = X.shape[0]
    cdef Py_ssize_t d = X.shape[1]
    if d == 1 and metric == "precomputed":
        n = <Py_ssize_t>libc.math.round((libc.math.sqrt(1.0+8.0*n)+1.0)/2.0)
        assert n*(n-1)//2 == X.shape[0]
    cdef Py_ssize_t i
    cdef np.ndarray[Py_ssize_t,ndim=2] mst_ind  = np.empty((n-1, 2), dtype=np.intp)
    cdef np.ndarray[floatT]         mst_dist = np.empty(n-1,
        dtype=np.float32 if floatT is float else np.float64)
    cdef c_mst.CDistance[floatT]* D = NULL
    cdef c_mst.CDistance[floatT]* D2 = NULL

    if metric == "euclidean" or metric == "l2":
        D = <c_mst.CDistance[floatT]*>new c_mst.CDistanceEuclidean[floatT](&X[0,0], n, d)
    elif metric == "manhattan" or metric == "cityblock" or metric == "l1":
        D = <c_mst.CDistance[floatT]*>new c_mst.CDistanceManhattan[floatT](&X[0,0], n, d)
    elif metric == "cosine" or metric == "cosinesimil":
        D = <c_mst.CDistance[floatT]*>new c_mst.CDistanceCosine[floatT](&X[0,0], n, d)
    elif metric == "precomputed":
        if d == 1:
            D = <c_mst.CDistance[floatT]*>new c_mst.CDistancePrecomputedVector[floatT](&X[0,0], n)
        else:
            assert d == n
            D = <c_mst.CDistance[floatT]*>new c_mst.CDistancePrecomputedMatrix[floatT](&X[0,0], n)
    else:
        raise NotImplementedError("given `metric` is not supported (yet)")

    if d_core is not None:
        D2 = D # must be deleted separately
        D  = <c_mst.CDistance[floatT]*>new c_mst.CDistanceMutualReachability[floatT](&d_core[0], n, D2)

    _openmp_set_num_threads()
    c_mst.Cmst_from_complete(D, n, &mst_dist[0], &mst_ind[0,0], verbose)

    if D:  del D
    if D2: del D2

    return mst_dist, mst_ind