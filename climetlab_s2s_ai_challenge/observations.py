from __future__ import annotations

import climetlab as cml
from climetlab.normalize import normalize_args

from . import DATA, DATA_VERSION, URL
from .s2s_dataset import S2sDataset

PATTERN_OBS = "{url}/{data}/forecast-input-dev/eccc-forecast/0.2.6/netcdf/eccc-forecast-{parameter}-{date}.nc"
# PATTERN_OBS = "{url}/{data}/{dataset}/{origin}-{fctype}/{version}/grib/{origin}-{fctype}-{parameter}-{date}.grib"


class Observations(S2sDataset):

    dataset = None

    terms_of_use = (
        "By downloading data from this dataset, you agree to the terms and conditions defined at "
        "https://apps.ecmwf.int/datasets/data/s2s/licence/. "
        "If you do not agree with such terms, do not download the data. "
    ) + (" This dataset has been dowloaded from IRIDL.")

    def __init__(self, version=DATA_VERSION):
        self.version = version

    @normalize_args(parameter="variable-list(cf)", date="date-list(%Y%m%d)")
    def _make_request(self, parameter, date):
        request = dict(url=URL, data=DATA, date=date, parameter=parameter)
        return request

    def _load(self, *args, **kwargs):
        request = self._make_request(*args, **kwargs)
        self.source = cml.load_source("url-pattern", PATTERN_OBS, request)


dataset = Observations
