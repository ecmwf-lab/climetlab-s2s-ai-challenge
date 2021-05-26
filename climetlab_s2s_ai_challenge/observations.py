from __future__ import annotations

import climetlab as cml
from climetlab.normalize import normalize_args

from . import DATA, DATA_VERSION, URL
from .fields import S2sMerger
from .s2s_dataset import S2sDataset

PATTERN_OBS = "{url}/{data}/{dataset}/{parameter}-{date}.nc"


class Observations(S2sDataset):

    terms_of_use = (
        "By downloading data from this dataset, you agree to the terms and conditions defined at "
        "https://apps.ecmwf.int/datasets/data/s2s/licence/. "
        "If you do not agree with such terms, do not download the data. "
    ) + (
        " This dataset has been dowloaded from IRIDL. By downloading this data you also agree to "
        "the terms and conditions defined at https://iridl.ldeo.columbia.edu."
    )

    @normalize_args(parameter="variable-list(cf)", date="date-list(%Y%m%d)")
    def __init__(self, dataset, parameter, date=None, version=DATA_VERSION):
        self.dataset = dataset
        self.version = version
        self.date = date
        self.parameter = parameter

        request = self._make_request()
        self.source = cml.load_source("url-pattern", PATTERN_OBS, request, merger=S2sMerger(engine="netcdf4"))

    def _make_request(self):
        request = dict(
            url=URL,
            data=DATA,
            parameter=self.parameter,
            dataset=self.dataset,
            date=self.date,
        )
        return request


class TrainingOutputReference(Observations):
    def __init__(self, *args, **kwargs):
        Observations.__init__(self, *args, dataset="training-output-reference", **kwargs)


class TestOutputReference(Observations):
    def __init__(self, *args, **kwargs):
        Observations.__init__(self, *args, dataset="test-output-reference", **kwargs)


HindcastLikeObservations = TrainingOutputReference
ForecastLikeObservations = TestOutputReference
