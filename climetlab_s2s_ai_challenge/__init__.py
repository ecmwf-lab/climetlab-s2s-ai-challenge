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
__version__ = "0.4.15"
DATA_VERSION = "0.2.5"

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


def roundtrip(ds, strict_check=True, copy_filename=None, verbose=False):
    import xarray as xr

    if copy_filename is None or copy_filename is False:
        # import uuid
        # uniq = uuid.uuid4()
        # copy_filename = f"test_{uniq}.nc"

        import os
        import tempfile

        fd, copy_filename = tempfile.mkstemp()
        os.close(fd)
    coords = " ".join(sorted(list(ds.coords)))
    ds.to_netcdf(copy_filename)
    copy = xr.open_dataset(copy_filename)
    coords2 = " ".join(sorted(list(copy.coords)))
    if verbose:
        print(f"{copy_filename} :\n  in = {coords} \n  out= {coords2}")
    if strict_check and coords != coords2:
        raise (Exception(f"Round trip failed seed {copy_filename}"))
    return copy


def ensure_naming_conventions(ds, round_trip_hack=False):  # noqa C901
    # we may want also to add this too :
    # import cf2cdm # this is from the package cfgrib
    # ds = cf2cdm.translate_coords(ds, cf2cdm.CDS)
    # or
    # ds = cf2cdm.translate_coords(ds, cf2cdm.ECMWF)

    if "number" in list(ds.coords):
        ds = ds.rename({"number": "realization"})

    if "depth_below_and_layer" not in list(ds.coords) and "depthBelowLandLayer" in list(
        ds.coords
    ):
        ds = ds.rename({"depthBelowLandLayer": "depth_below_and_layer"})

    if "entire_atmosphere" not in list(ds.coords) and "entireAtmospheretime" in list(
        ds.coords
    ):
        ds = ds.rename({"entireAtmosphere": "entire_atmosphere"})

    if "nominal_top" not in list(ds.coords) and "nominalTop" in list(ds.coords):
        ds = ds.rename({"nominalTop": "nominal_top"})

    if "forecast_time" not in list(ds.coords) and "time" in list(ds.coords):
        ds = ds.rename({"time": "forecast_time"})

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

    if round_trip_hack:  # see https://github.com/pydata/xarray/issues/5170
        ds = roundtrip(ds, strict_check=False, copy_filename=round_trip_hack)
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


def training_input(
    format="grib", origin="ecmwf", fctype="hindcast", version=DATA_VERSION
):
    return CLASSES[format](
        origin=origin, version=version, dataset="training-input", fctype=fctype
    )


def training_input_dev(
    format="grib", origin="ecmwf", fctype="hindcast", version=DATA_VERSION
):
    return CLASSES[format](
        origin=origin, version=version, dataset="training-input-dev", fctype=fctype
    )


def forecast_input(
    format="grib", origin="ecmwf", fctype="forecast", version=DATA_VERSION
):
    return CLASSES[format](
        origin=origin, version=version, dataset="forecast-input", fctype=fctype
    )


def forecast_input_dev(
    format="grib", origin="ecmwf", fctype="forecast", version=DATA_VERSION
):
    return CLASSES[format](
        origin=origin, version=version, dataset="forecast-input-dev", fctype=fctype
    )
