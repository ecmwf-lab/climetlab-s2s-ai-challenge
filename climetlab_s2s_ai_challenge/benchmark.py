# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from __future__ import annotations

import climetlab as cml
from climetlab import Dataset

from . import DATA, URL
from .extra import cf_conventions

PATTERN = "{url}/{data}/{dataset}/{parameter}.nc"


def benchmark_builder(datasetname):
    class Benchmark(Dataset):
        terms_of_use = (
            "By downloading data from this dataset, you agree to the terms and conditions defined at "
            "https://apps.ecmwf.int/datasets/data/s2s/licence/. "
            "If you do not agree with such terms, do not download the data. "
        )

        # valid_parameters = ["t2m", "tp"]

        def __init__(self, parameter):
            parameter = cf_conventions(parameter)
            self.dataset = datasetname
            request = dict(url=URL, data=DATA, parameter=parameter, dataset=self.dataset)
            self.source = cml.load_source(
                "url-pattern",
                PATTERN,
                request,
                merger="merge()",
            )

    return Benchmark


TestOutputBenchmark = benchmark_builder("test-output-benchmark")
TrainingOutputBenchmark = benchmark_builder("training-output-benchmark")

ForecastBenchmark = TestOutputBenchmark
HindcastBenchmark = TrainingOutputBenchmark
