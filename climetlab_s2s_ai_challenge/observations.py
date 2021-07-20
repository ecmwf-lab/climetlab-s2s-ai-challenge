from __future__ import annotations

import climetlab as cml
import xarray as xr
from climetlab.normalize import normalize_args

from . import DATA, OBSERVATIONS_DATA_VERSION, URL, S2sVariableMerger
from .fields import S2sMerger
from .s2s_dataset import S2sDataset

PATTERN_OBS = "{url}/{data}/{dataset}/{version}/{parameter}-{date}.nc"
PATTERN_RAWOBS = "{url}/{data}/{dataset}/{version}/{parameter}{grid_string}.nc"

GRID_STRING = {
    "240x121": "",
    "121x240": "",
    "720x360": "_720x360",
    "360x720": "_720x360",
}


class Observations(S2sDataset):
    terms_of_use = (
        "By downloading data from this dataset, you agree to the terms and conditions defined at "
        "https://apps.ecmwf.int/datasets/data/s2s/licence/. "
        "If you do not agree with such terms, do not download the data. "
    ) + (
        " This dataset has been dowloaded from IRIDL. By downloading this data you also agree to "
        "the terms and conditions defined at https://iridl.ldeo.columbia.edu."
    )


class RawObservations(Observations):
    PARAMETERS = ["t2m", "pr"]

    def __init__(self, parameter, grid="240x121", version=OBSERVATIONS_DATA_VERSION):
        self.dataset = "observations"
        self.version = version
        self.grid_string = GRID_STRING[grid]

        if not isinstance(parameter, list):
            parameter = [parameter]
        for p in parameter:
            if p not in self.PARAMETERS:
                raise KeyError(f"Parameter {p} unknown. Available values are {self.PARAMETERS}")

        request = dict(
            url=URL,
            data=DATA,
            parameter=parameter,
            dataset=self.dataset,
            version=self.version,
            grid_string=self.grid_string,
        )
        self.source = cml.load_source("url-pattern", PATTERN_RAWOBS, request, merger=S2sVariableMerger())

    def to_xarray(self, like=None):
        ds = self.source.to_xarray()
        if isinstance(like, xr.Dataset):
            from .extra import forecast_like_observations

            ds = forecast_like_observations(like, ds)
        return ds


class PreprocessedObservations(Observations):
    @normalize_args(parameter="variable-list(cf)", date="date-list(%Y%m%d)")
    def __init__(self, dataset, parameter, date=None, version=OBSERVATIONS_DATA_VERSION):
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
            version=self.version,
        )
        return request


class TrainingOutputReference(PreprocessedObservations):
    def __init__(self, *args, **kwargs):
        PreprocessedObservations.__init__(self, *args, dataset="training-output-reference", **kwargs)


class TestOutputReference(PreprocessedObservations):
    def __init__(self, *args, **kwargs):
        PreprocessedObservations.__init__(self, *args, dataset="test-output-reference", **kwargs)


HindcastLikeObservations = TrainingOutputReference
ForecastLikeObservations = TestOutputReference
