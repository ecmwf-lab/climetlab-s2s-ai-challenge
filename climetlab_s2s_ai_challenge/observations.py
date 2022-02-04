# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from __future__ import annotations

import climetlab as cml
import xarray as xr
from climetlab.decorators import normalize
from climetlab.normalize import normalize_args

from . import DATA, OBSERVATIONS_DATA_VERSION, URL, S2sDataset
from .s2s_mergers import ensure_naming_conventions

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
    dataset = "observations"

    @normalize("parameter", [None, "t2m", "pr"], multiple=True)
    def __init__(self, parameter=None, grid="240x121", version=OBSERVATIONS_DATA_VERSION):
        if parameter == [None] or parameter is None:
            parameter = ["t2m", "pr"]
        self.version = version
        self.grid_string = GRID_STRING[grid]

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

    @normalize_args(date="date-list(%Y%m%d)")
    @normalize("parameter", [None, "t2m", "tp"], multiple=True)
    def __init__(self, date, parameter=None, version=OBSERVATIONS_DATA_VERSION):
        if parameter == [None] or parameter is None:
            parameter = ["t2m", "pr"]
        self.version = version
        self.date = date
        self.parameter = parameter

        sources = []
        for p in parameter:
            request = self._make_request(p)
            sources.append(
                cml.load_source("url-pattern", PATTERN_OBS, request, merger="concat(concat_dim=time_forecast)")
            )
        self.source = cml.load_source("multi", sources, merger="merge()")

    def to_xarray(self, *args, **kwargs):
        ds = self.source.to_xarray()
        ds = ensure_naming_conventions(ds)
        return ds

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
