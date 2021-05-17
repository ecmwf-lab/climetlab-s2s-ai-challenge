from __future__ import annotations

import climetlab as cml
from climetlab import Dataset
from climetlab.normalize import normalize_args

from . import DATA, URL

PATTERN = "{url}/{data}/{dataset}/{parameter}.W{weeks}.nc"


class TestOutputBenchmark(Dataset):

    terms_of_use = (
        "By downloading data from this dataset, you agree to the terms and conditions defined at "
        "https://apps.ecmwf.int/datasets/data/s2s/licence/. "
        "If you do not agree with such terms, do not download the data. "
    )

    def __init__(self):
        self.dataset = "test-output-benchmark"

    @normalize_args(
        parameter=["t2p", "tp"],
        weeks=["34", "56"],
        #  start_year=[2002])
    )
    def _make_request(self, parameter, weeks):
        request = dict(url=URL, data=DATA, weeks=weeks, parameter=parameter, dataset=self.dataset)
        return request

    def _load(self, parameter, weeks, *args, **kwargs):
        request = self._make_request(parameter=parameter, weeks=weeks, *args, **kwargs)
        self.source = cml.load_source("url-pattern", PATTERN, request)


ForecastBenchmark = TestOutputBenchmark
