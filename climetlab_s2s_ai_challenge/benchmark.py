from __future__ import annotations

import climetlab as cml
from climetlab import Dataset
from climetlab.normalize import normalize_args

from . import DATA, URL
from .fields import S2sMerger

PATTERN = "{url}/{data}/{dataset}/{parameter}-weeks-{weeks}.nc"


def benchmark_builder(datasetname):
    class Benchmark(Dataset):

        terms_of_use = (
            "By downloading data from this dataset, you agree to the terms and conditions defined at "
            "https://apps.ecmwf.int/datasets/data/s2s/licence/. "
            "If you do not agree with such terms, do not download the data. "
        )

        @normalize_args(
            parameter="variable-list(cf)",
            weeks=["34", "56", ["34"], ["56"], ["34", "56"]],
        )
        def __init__(self, parameter, weeks):
            self.dataset = datasetname
            request = dict(url=URL, data=DATA, weeks=weeks, parameter=parameter, dataset=self.dataset)
            self.source = cml.load_source(
                "url-pattern",
                PATTERN,
                request,
                merger=S2sMerger(engine="netcdf4", concat_dim="weeks"),
            )

    return Benchmark


TestOutputBenchmark = benchmark_builder("test-output-benchmark")
TrainingOutputBenchmark = benchmark_builder("training-output-benchmark")

ForecastBenchmark = TestOutputBenchmark
HindcastBenchmark = TrainingOutputBenchmark
