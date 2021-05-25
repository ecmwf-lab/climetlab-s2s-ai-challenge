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

    @normalize_args(parameter="variable-list(cf)", date="date-list(%Y%m%d)", start_year=[2000])
    def __init__(self, dataset, parameter, date=None, freq=None, version=DATA_VERSION, start_year=START_YEAR):
        self.dataset = dataset
        self.version = version
        self.date = date
        self.parameter = parameter
        self.freq = freq
        self.start_year = start_year

        request = self._make_request()
        self.source = cml.load_source("url-pattern", PATTERN_OBS, request)

    def _make_request(self):
        request = dict(
            url=URL,
            data=DATA,
            freq=self.freq,
            parameter=self.parameter,
            start_year=self.start_year,
            dataset=self.dataset,
            date=self.date,
        )
        return request


class TrainingOutputReference(Observations):
    def __init__(self, *args, freq="weekly", **kwargs):
        Observations.__init__(self, *args, dataset="training-output-reference", freq=freq, **kwargs)


class TestOutputReference(Observations):
    def __init__(self, *args, freq="daily", **kwargs):
        Observations.__init__(self, *args, dataset="test-output-reference", freq=freq, **kwargs)


HindcastLikeObservations = TrainingOutputReference
ForecastLikeObservations = TestOutputReference
