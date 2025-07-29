"""
<tribal> Package
"""


import setuptools
from setuptools.command.sdist import sdist
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import numpy as np
import os.path
import glob
import os
import sys
import re

# genieclust MST-specific
ext_kwargs = dict(
    include_dirs=[np.get_include(),], #"tribal/algorithms/src/genieclust_mst_src", "../src/"],
    language="c++",
)

PATH_GENIECLUST_MST = "./tribal/algorithms/src/genieclust/"
PATH_MSTL = "./tribal/algorithms/src/mstl/source/"
PATH_GMKNN = "./tribal/algorithms/src/gmknn/source/"
PATH_TDBSCAN = "./tribal/algorithms/src/tdbscan/source/"

DEST_PATH_GENICLUST_MST = "tribal.algorithms.src.genieclust."
DEST_PATH_MSTL = "tribal.algorithms.src.mstl.binaries."
DEST_PATH_GMKNN = "tribal.algorithms.src.gmknn.binaries."
DEST_PATH_TDBSCAN = "tribal.algorithms.src.tdbscan.binaries."


GENIECLUST_MODULES = (
    "genieclustering_mst",
)
MSTL_MODULES = (
    "mstl_mst",
    "mstl_core",
)
GMKNN_MODULES = (
    "mknn",
    "gmknn_bfs",
    "gmknn_connect",
    "gmknn_lp",
)
TDBSCAN_MODULES = (
    "tdbscan_core",
    "tdbscan_postprocess",
)

GENIECLUST_module_list = [PATH_GENIECLUST_MST + mod + ".pyx" for mod in GENIECLUST_MODULES]
MSTL_module_list = [PATH_MSTL + mod + ".pyx" for mod in MSTL_MODULES]
GMKNN_module_list = [PATH_GMKNN + mod + ".pyx" for mod in GMKNN_MODULES]
TDBSCAN_module_list = [PATH_TDBSCAN + mod + ".pyx" for mod in TDBSCAN_MODULES]


GENIECLUST_MST_extensions_list = [setuptools.Extension(DEST_PATH_GENICLUST_MST + module, [pyx_module], **ext_kwargs) for module,pyx_module
                         in zip(GENIECLUST_MODULES, GENIECLUST_module_list)]

MSTL_extensions_list = [setuptools.Extension(DEST_PATH_MSTL + module, [pyx_module]) for module,pyx_module
                         in zip(MSTL_MODULES, MSTL_module_list)]

GMKNN_extensions_list = [setuptools.Extension(DEST_PATH_GMKNN + module, [pyx_module]) for module,pyx_module
                         in zip(GMKNN_MODULES, GMKNN_module_list)]

TDBSCAN_extensions_list = [setuptools.Extension(DEST_PATH_TDBSCAN + module, [pyx_module]) for module,pyx_module
                         in zip(TDBSCAN_MODULES, TDBSCAN_module_list)]


extensions_list = [] + MSTL_extensions_list + GMKNN_extensions_list + TDBSCAN_extensions_list + GENIECLUST_MST_extensions_list


class genieclust_sdist(sdist):
    def run(self):
        cythonize(extensions_list, 
                  language_level="3",)
        sdist.run(self)


class genieclust_build_ext(build_ext):
    def build_extensions(self):
        build_ext.build_extensions(self)




with open("README.md", "r") as fh:
    long_description = fh.read()

__version__ = "0.1.5"
setuptools.setup(
    name="tribal",
    version=__version__,
    license="GNU Affero General Public License v3",
    install_requires=[
        "numpy",
        "scipy",
        "Cython", 
        "matplotlib",
        "scikit-learn",
        "networkx",
      ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url="https://github.com/WojtekGrbs/tribal",
    url="https://github.com/WojtekGrbs/tribal",

    project_urls={
        "Source Code":        "https://github.com/WojtekGrbs/tribal",
        "Benchmark Datasets": "https://clustering-benchmarks.gagolewski.com/",
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Topic :: Scientific/Engineering",
    ],
    cmdclass={
        "sdist": genieclust_sdist,
        "build_ext": genieclust_build_ext
    },
    packages=setuptools.find_packages(include=["tribal*", ]),  # Automatically find packages in the current directory
    # package_dir={"": "tribal"},  # Map the root directory of packages to "tribal/"
    ext_modules=extensions_list,
    include_dirs=[np.get_include(),] # "tribal/algorithms/src/genieclust_mst_src"]
)
