from __future__ import annotations

import climetlab as cml
from climetlab.normalize import normalize_args

from . import DATA, DATA_VERSION, URL
from .s2s_dataset import S2sDataset

START_YEAR = 2002
PATTERN_OBS = "{url}/{data}/{dataset}/{parameter}-{freq}-since-{start_year}.nc"


class Observations(S2sDataset):

    terms_of_use = (
        "By downloading data from this dataset, you agree to the terms and conditions defined at "
        "https://apps.ecmwf.int/datasets/data/s2s/licence/. "
        "If you do not agree with such terms, do not download the data. "
    ) + (" This dataset has been dowloaded from IRIDL.")

    # @normalize_args(date="date-list(%Y%m%d)")
    def __init__(self, date=None, version=DATA_VERSION):
        self.dataset = "observations"
        self.version = version
        self.date = date

    @normalize_args(
        parameter=["t2m", "tp", "pr"],
        freq=["daily", "weekly"]
        #  start_year=[2002])
    )
    def _make_request(self, parameter, freq="daily", start_year=START_YEAR):
        request = dict(
            url=URL,
            data=DATA,
            freq=freq,
            parameter=parameter,
            start_year=START_YEAR,
            dataset=self.dataset,
        )
        return request

    def _load(self, *args, **kwargs):
        request = self._make_request(*args, **kwargs)
        self.source = cml.load_source("url-pattern", PATTERN_OBS, request)


class ObservationsDev(Observations):
    def __init__(self, *args, **kwargs):
        super(ObservationsDev, self).__init__(*args, **kwargs)
        self.dataset = "observations-dev"
