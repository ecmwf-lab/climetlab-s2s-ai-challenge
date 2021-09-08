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
