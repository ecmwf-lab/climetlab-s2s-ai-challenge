from __future__ import annotations

import climetlab as cml
from climetlab import Dataset
from climetlab.normalize import normalize_args

from . import DATA, URL

PATTERN = "{url}/{data}/{dataset}/{parameter}-weeks-{weeks}.nc"


class TestOutputBenchmark(Dataset):

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
        self.dataset = "test-output-benchmark"
        request = dict(url=URL, data=DATA, weeks=weeks, parameter=parameter, dataset=self.dataset)
        self.source = cml.load_source("url-pattern", PATTERN, request)


#    def to_xarray(self, *args, **kwargs):
#        return self.source.to_xarray()


ForecastBenchmark = TestOutputBenchmark
