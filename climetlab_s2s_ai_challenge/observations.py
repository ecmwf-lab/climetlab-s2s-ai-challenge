from __future__ import annotations

import climetlab as cml
from climetlab.normalize import normalize_args

from . import DATA, DATA_VERSION, URL
from .s2s_dataset import S2sDataset

START_YEAR = 2000
PATTERN_OBS = "{url}/{data}/{dataset}/{parameter}/{freq}-since-{start_year}/{date}.nc"


class Observations(S2sDataset):

    terms_of_use = (
        "By downloading data from this dataset, you agree to the terms and conditions defined at "
        "https://apps.ecmwf.int/datasets/data/s2s/licence/. "
        "If you do not agree with such terms, do not download the data. "
    ) + (
        " This dataset has been dowloaded from IRIDL. By downloading this data you also agree to "
        "the terms and conditions defined at https://iridl.ldeo.columbia.edu."
    )

    # @normalize_args(date="date-list(%Y%m%d)")
    def __init__(self, version=DATA_VERSION):
        self.dataset = None
        self.version = version

    @normalize_args(
        parameter=["t2m", "tp"],
        #  start_year=[2002])
    )
    def _make_request(self, parameter, date, freq=None, start_year=START_YEAR):
        if freq is None:
            freq = self.freq
        request = dict(
            url=URL, data=DATA, freq=freq, parameter=parameter, start_year=START_YEAR, dataset=self.dataset, date=date
        )
        return request

    def _load(self, date, *args, **kwargs):
        request = self._make_request(date=date, *args, **kwargs)
        self.source = cml.load_source("url-pattern", PATTERN_OBS, request)


class TrainingOutputReference(Observations):
    def __init__(self, *args, **kwargs):
        Observations.__init__(self, *args, **kwargs)
        self.dataset = "training-output-reference"
        self.freq = "weekly"


class TestOutputReference(Observations):
    def __init__(self, *args, **kwargs):
        Observations.__init__(self, *args, **kwargs)
        self.dataset = "test-output-reference"
        self.freq = "daily"


HindcastLikeObservations = TrainingOutputReference
ForecastLikeObservations = TestOutputReference
