# (C) Copyright 2020 ECMWF.  #
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from __future__ import annotations

import climetlab as cml
from climetlab import Dataset
from climetlab.normalize import normalize_args
from climetlab.utils.conventions import normalise_string

# note : this version number is the plugin version. It has nothing to do with the version number of the dataset
__version__ = "0.4.13"
DATA_VERSION = "0.2.3"

URL = "https://storage.ecmwf.europeanweather.cloud"
DATA = "s2s-ai-challenge/data"

# fmt:off
PATTERN_GRIB = "{url}/{data}/{dataset}/{origin}-{fctype}/{version}/grib/{origin}-{fctype}-{parameter}-{date}.grib"
PATTERN_NCDF = "{url}/{data}/{dataset}/{origin}-{fctype}/{version}/netcdf/{origin}-{fctype}-{parameter}-{date}.nc"
PATTERN_ZARR = "{url}/{data}/{dataset}/{origin}-{fctype}/{version}/zarr/{parameter}.zarr"
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


class S2sDataset(Dataset):
    name = None
    home_page = "-"
    licence = "https://apps.ecmwf.int/datasets/data/s2s/licence/"
    # TODO : upload a json file next to the dataset and read it
    documentation = "-"
    citation = "-"

    terms_of_use = (
        "By downloading data from this dataset, you agree to the terms and conditions defined at "
        "https://apps.ecmwf.int/datasets/data/s2s/licence/. "
        "If you do not agree with such terms, do not download the data. "
    )

    dataset = None

    def __init__(self, origin, version, dataset, fctype):
        self.origin = ALIAS_ORIGIN[origin.lower()]
        self.fctype = ALIAS_FCTYPE[fctype.lower()]
        self.version = version
        self.dataset = dataset

    @normalize_args(parameter="variable-list(cf)", date="date-list(%Y%m%d)")
    def _make_request(
        self,
        date="20200102",
        parameter="tp",
        hindcast=False,
    ):
        request = dict(
            url=URL,
            data=DATA,
            dataset=self.dataset,
            origin=self.origin,
            version=self.version,
            parameter=parameter,
            fctype=self.fctype,
            date=date,
        )
        return request

    def post_xarray_open_dataset_hook(self, ds):
        return ensure_naming_conventions(ds)


def ensure_naming_conventions(ds):  # noqa C901
    # we may want also to add this too :
    # import cf2cdm # this is from the package cfgrib
    # ds = cf2cdm.translate_coords(ds, cf2cdm.CDS)
    # or
    # ds = cf2cdm.translate_coords(ds, cf2cdm.ECMWF)

    if "number" in list(ds.coords):
        ds = ds.rename({"number": "realization"})

    # added after building data v 0.1.43
    if "depth_below_and_layer" not in list(ds.coords) and "depthBelowLandLayer" in list(
        ds.coords
    ):
        ds = ds.rename({"depthBelowLandLayer": "depth_below_and_layer"})

    # added after building data v 0.1.43
    if "entire_atmosphere" not in list(ds.coords) and "entireAtmospheretime" in list(
        ds.coords
    ):
        ds = ds.rename({"entireAtmosphere": "entire_atmosphere"})

    # added after building data v 0.1.43
    if "nominal_top" not in list(ds.coords) and "nominalTop" in list(ds.coords):
        ds = ds.rename({"nominalTop": "nominal_top"})

    if "forecast_time" not in list(ds.coords) and "time" in list(ds.coords):
        ds = ds.rename({"time": "forecast_time"})

    # added after building data v 0.1.43
    if "valid_time" not in list(ds.variables) and "time" in list(ds.variables):
        ds = ds.rename({"time": "valid_time"})

    if "step" in list(ds.coords) and "lead_time" not in list(ds.coords):
        ds = ds.rename({"step": "lead_time"})

    if "isobaricInhPa" in list(ds.coords):
        ds = ds.rename({"isobaricInhPa": "plev"})

    # if "plev" in list(ds.coords) and len(ds.coords['plev']) <= 1:
    #    ds = ds.squeeze("plev")
    #    ds = ds.drop("plev")

    if "surface" in list(ds.coords):
        ds = ds.squeeze("surface")
        ds = ds.drop_vars("surface")

    if "heightAboveGround" in list(ds.coords):
        ds = ds.rename({"heightAboveGround": "height_above_ground"})

    if (
        "height_above_ground" in list(ds.coords)
        and len(ds.coords["height_above_ground"]) <= 1
    ):
        ds = ds.squeeze("height_above_ground")
        ds = ds.drop("height_above_ground")

    # added after building data v 0.1.43
    if "valid_time" in list(ds.variables) and "valid_time" not in list(ds.coords):
        ds = ds.set_coords("valid_time")

    for name in list(ds.variables):
        ds = ds.rename({name: normalise_string(name, convention="cf")})

    return ds


class S2sDatasetGRIB(S2sDataset):
    def _load(self, *args, **kwargs):
        request = self._make_request(*args, **kwargs)
        self.source = cml.load_source("url-pattern", PATTERN_GRIB, request)

    def cfgrib_options(self, time_convention="withstep"):
        params = {}
        assert time_convention in ("withstep", "nostep")

        if time_convention == "withstep":
            time_dims = ["time", "step"]  # this is the default of engine='cfgrib'
            chunk_sizes_in = {
                "time": 1,
                "latitude": None,
                "longitude": None,
                "number": 1,
                "step": 1,
            }

        if time_convention == "nostep":
            time_dims = ["time", "valid_time"]
            chunk_sizes_in = {
                "time": 1,
                "latitude": None,
                "longitude": None,
                "number": 1,
                "valid_time": 1,
            }

        params["chunks"] = chunk_sizes_in
        params["backend_kwargs"] = dict(squeeze=False, time_dims=time_dims)

        return params


class S2sDatasetNETCDF(S2sDataset):
    def _load(self, *args, **kwargs):
        request = self._make_request(*args, **kwargs)
        self.source = cml.load_source("url-pattern", PATTERN_NCDF, request)


class S2sDatasetZARR(S2sDataset):
    def _load(self, *args, **kwargs):

        from climetlab.utils.patterns import Pattern

        request = self._make_request(*args, **kwargs)
        request.pop("date")

        urls = Pattern(PATTERN_ZARR).substitute(request)

        self.source = cml.load_source("zarr-s3", urls)


CLASSES = {"grib": S2sDatasetGRIB, "netcdf": S2sDatasetNETCDF, "zarr": S2sDatasetZARR}


class Info:
    def __init__(self, dataset):
        import os

        import yaml

        self.dataset = dataset
        filename = self.dataset.replace("-", "_") + ".yaml"
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(path) as f:
            self.config = yaml.unsafe_load(f.read())

    def _get_cf_name(self, param):
        return cml.utils.conventions.normalise_string(param, convention="cf")

    # TODO add _
    def get_category_param(self, param):
        if param in "2t/sst/sm20/sm100/st20/st100/ci/rsn/tcc/tcw".split("/"):
            return "daily_average"
        if param in "sp/msl/ttr/tp".split("/"):
            return "instantaneous"
        if param in "lsm".split("/"):
            return "instantaneous_only_control"
        if param in "u/v/gh/t".split("/"):
            return "3d"
        if param in "q".split("/"):
            return "3dbis"
        raise NotImplementedError(param)

    def _get_config_keys(self):
        return self.config.keys()

    def _get_s3path_grib(
        self, origin, fctype, parameter, date, url="s3://", version=DATA_VERSION
    ):
        return PATTERN_GRIB.format(
            url=url,
            data="s2s-ai-challenge/data",
            dataset=self.dataset,
            fctype=fctype,
            origin=origin,
            version=version,
            parameter=parameter,
            date=date,
        )

    def _get_s3path_netcdf(
        self, origin, fctype, parameter, date, url="s3://", version=DATA_VERSION
    ):
        return PATTERN_NCDF.format(
            url=url,
            data="s2s-ai-challenge/data",
            dataset=self.dataset,
            fctype=fctype,
            origin=origin,
            version=version,
            parameter=parameter,
            date=date,
        )

    def _get_config(self, key, origin, fctype, date=None, param=None):
        origin_fctype = f"{origin}-{fctype}"

        import pandas as pd

        if key == "hdate":
            if origin == "ncep" and fctype == "hindcast":
                return pd.date_range(end=date, periods=12, freq=pd.DateOffset(years=1))

        if key == "marsdate":
            if origin == "ncep" and fctype == "hindcast":
                only_one_date = "2011-03-01"
                return pd.to_datetime(only_one_date)
            else:
                return date

        if param is None:
            return self.config[origin_fctype][key]
        return self.config[origin_fctype][param][key]


def dataset(dataset, *args, **kwargs):
    return CLASSES[format](*args, **kwargs)
