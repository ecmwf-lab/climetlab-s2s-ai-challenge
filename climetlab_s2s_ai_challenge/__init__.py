# (C) Copyright 2020 ECMWF.  #
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from __future__ import annotations

import xarray as xr

from . import extra  # noqa F401

# note : this version number is the plugin version. It has nothing to do with the version number of the dataset
__version__ = "0.7.6"
DATA_VERSION = "0.3.0"
OBSERVATIONS_DATA_VERSION = "0.3.1"

URL = "https://storage.ecmwf.europeanweather.cloud"
DATA = "s2s-ai-challenge/data"

# fmt:off
PATTERN_GRIB = "{url}/{data}/{dataset}/{version}/grib/{origin}-{fctype}-{parameter}-{date}.grib"
PATTERN_NCDF = "{url}/{data}/{dataset}/{version}/netcdf/{origin}-{fctype}-{parameter}-{date}.nc"
PATTERN_ZARR = "{url}/{data}/{dataset}/{version}/zarr/{origin}-{fctype}-{parameter}.zarr"
# fmt:on

ALIAS_ORIGIN = {
    "ecmwf": "ecmwf",
    "ecmf": "ecmwf",
    "cwao": "eccc",
    "eccc": "eccc",
    "kwbc": "ncep",
    "ncep": "ncep",
}

ALIAS_MARSORIGIN = {
    "ecmwf": "ecmf",
    "ecmf": "ecmf",
    "cwao": "cwao",
    "eccc": "cwao",
    "kwbc": "kwbc",
    "ncep": "kwbc",
}

ALIAS_FCTYPE = {
    "hindcast": "hindcast",
    "reforecast": "hindcast",
    "forecast": "forecast",
    "realtime": "forecast",
    "hc": "hindcast",
    "rt": "forecast",
    "fc": "forecast",
}

CF_CELL_METHODS = {
    "t2p": None,
    "tpp": None,
    "t2m": "average",
    "sst": "average",
    "siconc": "average",
    "rsn": "average",
    "tcc": "average",
    "tcw": "average",
    "sm20": "average",
    "sm100": "average",
    "st20": "average",
    "st100": "average",
    "tp": "sum",  # accumulated
    "ttr": "sum",  # accumulated
    "sp": "point",
    "msl": "point",
    "lsm": "point",
    "u": "point",
    "v": "point",
    "gh": "point",
    "t": "point",
    "q": "point",
}
#        'q': '3d', 'u':'3d','v':'3d','gh':'3d','t':'3d',


class S2sVariableMerger:
    def __init__(self, options=None):
        self.options = options if options is not None else {}

    def merge(self, paths, **kwargs):
        dslist = [xr.open_dataset(path) for path in paths]
        return xr.merge(dslist)
