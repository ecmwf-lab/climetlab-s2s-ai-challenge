#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import re

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

# See https://www.blog.pythonlibrary.org/2018/10/16/testing-jupyter-notebooks/


EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "notebooks")

SKIP = (
    "demo_zarr_experimental.ipynb",
    "demo_zarr.ipynb",
    "demo_forecast_benchmark.ipynb",
)


def notebooks_list():

    notebooks = []
    for path in os.listdir(EXAMPLES):
        if not path.startswith("demo_"):  # test only demo notebooks
            continue
        if not re.match(r"[^_].*\.ipynb$", path):  # ignore notebooks starting with '_'
            continue
        if "Copy" in path:  # ignore notebooks including 'Copy'
            continue
        if path.startswith("Untitled"):  # ignore untitled notebooks
            continue
        notebooks.append(path)

    return sorted(notebooks)


@pytest.mark.parametrize("path", notebooks_list())
def test_notebook(path):
    print(path)

    if path in SKIP:
        pytest.skip("Notebook marked as 'skip'")

    with open(os.path.join(EXAMPLES, path)) as f:
        nb = nbformat.read(f, as_version=4)

    proc = ExecutePreprocessor(timeout=60 * 60, kernel_name="python3")
    proc.preprocess(nb, {"metadata": {"path": EXAMPLES}})


if __name__ == "__main__":
    for k, f in sorted(globals().items()):
        if k.startswith("test_") and callable(f):
            print(k)
            f()
