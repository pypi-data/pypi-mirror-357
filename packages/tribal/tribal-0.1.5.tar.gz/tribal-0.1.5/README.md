# [**Tribal**](https://github.com/WojtekGrbs/tribal)
***Tr***ansductive ***i***nference-***b***ased clustering ***al***gorithms Python package

*Currently existing under the name tribal-temp, pending [PEP-541 approval from PyPi](https://github.com/pypi/support/issues/5567)* 
## About

Transatlantic is  a Python package containing
three clustering algorithms based on transductive inference for partially labeled data. The
goal of the algorithms is to enable determining the assignment of
input data to specific clusters based on existing labeled data.
Two of the proposed algorithms are based on graph constructions derived from the
input data, while the third relies solely on neighborhood proximity. The implementations
emphasize both computational efficiency and the ability for users to customize parameters.
The package also features an implementation of visualization methonds for two-dimensional or three-dimensional data.
The package was designed in a modular manner to facilitate future extensions and
updates. Additionally, the provided documentation and a set of practical examples
support users in quickly deploying the algorithms in real-world projects.

## Authors and Contributors

**Authors and Maintainers**: [Wojciech Grabias](https://github.com/WojtekGrbs), [Krzysztof Sawicki](https://github.com/SawickiK)<br>
**Guidance and contributions:** [prof. Marek Gągolewski](https://github.com/gagolews)
## How to Install

To install via `pip` (see [PyPI](https://pypi.org/project/tribal/)):

```bash
pip install tribal-temp
```
The package requires Python 3.8+ with dependiences listed bellow:
- Cython
- numpy
- scipy
- matplotlib
- scikit-learn
- networkx

## Example of use

All implemented algorithms can be imported via the path  `transatlantic.transductive_clustering`.  
These are the classes `MSTL`, `GMKNN`, and `TDBSCAN`.
```python
import tribal
from tribal.transductive_clustering import MSTL , GMKNN , TDBSCAN

alg1 = MSTL()
alg2 = GMKNN(k=7)
alg3 = TDBSCAN(eps=0.1, k=4, new_clusters=False)
```
The process is analogous to the scikit-learn package and is identical for each of the implemented algorithms.  
The user is required to provide data points as a list of lists or any other structure that can be cast to an object of the class `np.ndarray`, as well as initial labels as a one-dimensional list of integers (with the value `-1` used to indicate missing labels).  
The algorithm is executed on the provided data using the `fit()` method.
```bash
X = [[...] , [...] , ...] # Input data
y = [...] # Initial labels

alg1.fit(X , y)
```

To obtain the output labels of the algorithm, you should refer to the `labels_` attribute.
```python
final_labels = alg1.labels_
```

The two aforementioned steps can be combined into a single step by calling the `fit_predict()` method.
```bash
X = [[...] , [...] , ...] # Input data
y = [...] # Initial labels

final_labels = alg1.fit_predict(X , y)
```

### Additional functionalities related to algorithms

In the case of graph algorithms, it is possible to gain insight into the algorithm's execution by generating a graph that represents the graph responsible for the specific stages of the program.
```python
alg1.draw_transitional_graph("mst")
alg1.draw_result_graph()
```
In the case of the first algorithm, a minimum spanning tree is generated based on the initial data. For the second algorithm, the following options are available:
- knn - k-nearest neighbors graph
- mknn - mutual k-nearest neighbors graph
- informative edges - represents a stage aimed at removing insignificant edges
```python
alg2.draw_transitional_graph("knn") # Options : knn, gmknn ,informative_edges
alg2.draw_result_graph()
```
## Testing data

During the development of the project, the algorithms were tested on data from the [**Clustering Benchmark**](https://clustering-benchmarks.gagolewski.com/index.html) project.

## License

Transatlantic Package for Python

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License
Version 3, 19 November 2007, published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License Version 3 for more details.
You should have received a copy of the License along with this program.
If this is not the case, refer to <https://www.gnu.org/licenses/>.

## References

Gagolewski M., genieclust: Fast and robust hierarchical clustering,
*SoftwareX* **15**, 2021, 100722.
[DOI: 10.1016/j.softx.2021.100722](https://doi.org/10.1016/j.softx.2021.100722).
<https://genieclust.gagolewski.com/>.

Gagolewski M., A framework for benchmarking clustering algorithms,
*SoftwareX* **20**, 2022, 101270.
[DOI: 10.1016/j.softx.2022.101270](https://doi.org/10.1016/j.softx.2022.101270).
<https://clustering-benchmarks.gagolewski.com/>.
