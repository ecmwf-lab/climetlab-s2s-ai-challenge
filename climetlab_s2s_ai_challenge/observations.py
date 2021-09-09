from __future__ import annotations

import climetlab as cml
import xarray as xr
from climetlab.normalize import normalize_args

from . import DATA, OBSERVATIONS_DATA_VERSION, URL, S2sDataset
from .extra import cf_conventions
from .s2s_mergers import S2sMerger

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
        S2sDataset.terms_of_use
        + "\n"
        + (
            " This dataset has been dowloaded from IRIDL. By downloading this data you also agree to "
            "the terms and conditions defined at https://iridl.ldeo.columbia.edu."
        )
    )


class RawObservations(Observations):
    valid_parameters = ["t2m", "pr"]
    dataset = "observations"

    @normalize_args(parameter=valid_parameters)
    def __init__(self, parameter=None, grid="240x121", version=OBSERVATIONS_DATA_VERSION):
        self.version = version
        self.grid_string = GRID_STRING[grid]
        if parameter is None:
            parameter = self.valid_parameters
        parameter = cf_conventions(parameter)

        request = dict(
            url=URL,
            data=DATA,
            parameter=parameter,
            dataset=self.dataset,
            version=self.version,
            grid_string=self.grid_string,
        )

        self.source = cml.load_source("url-pattern", PATTERN_RAWOBS, request, merger="merge()")

    def to_xarray(self, like=None):
        ds = self.source.to_xarray()
        if isinstance(like, xr.Dataset):
            from .extra import forecast_like_observations

            ds = forecast_like_observations(like, ds)
        return ds


class PreprocessedObservations(Observations):
    dataset = None
    valid_parameters = ["t2m", "tp"]

    @normalize_args(date="date-list(%Y%m%d)", parameter=["t2m", "tp"])
    def __init__(self, date, parameter=None, version=OBSERVATIONS_DATA_VERSION):
        if parameter is None:
            parameter = self.valid_parameters
        parameter = cf_conventions(parameter)
        self.version = version
        self.date = date
        self.parameter = parameter

        sources = []
        for p in parameter:
            request = self._make_request(p)
            sources.append(
                cml.load_source("url-pattern", PATTERN_OBS, request, merger=S2sMerger(engine="netcdf4"))
                #  cml.load_source("url-pattern", PATTERN_OBS, request, merger=S2sMerger(engine="h5netcdf"))
                #  cml.load_source("url-pattern", PATTERN_OBS, request, merger='concat(concat_dim=time_forecast)')
            )
        self.source = cml.load_source("multi", sources, merger="merge()")

    def _make_request(self, parameter):
        request = dict(
            url=URL,
            data=DATA,
            parameter=parameter,
            dataset=self.dataset,
            date=self.date,
            version=self.version,
        )
        return request


class TrainingOutputReference(PreprocessedObservations):
    dataset = "training-output-reference"


class TestOutputReference(PreprocessedObservations):
    dataset = "test-output-reference"


HindcastLikeObservations = TrainingOutputReference
ForecastLikeObservations = TestOutputReference
