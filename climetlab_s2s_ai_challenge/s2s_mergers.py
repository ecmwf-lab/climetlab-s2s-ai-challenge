# (C) Copyright 2020 ECMWF.  #
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

import xarray as xr
from climetlab.utils.conventions import normalise_string

from . import CF_CELL_METHODS


def _roundtrip(ds, strict_check=True, copy_filename=None, verbose=False):

    if not copy_filename:
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

    if "t2p" in list(ds.variables) and "realization" in list(ds.coords):  # for benchmark dataset
        ds = ds.rename({"realization": "category"})

    if "depth_below_and_layer" not in list(ds.coords) and "depthBelowLandLayer" in list(ds.coords):
        ds = ds.rename({"depthBelowLandLayer": "depth_below_and_layer"})

    if "entire_atmosphere" not in list(ds.coords) and "entireAtmospheretime" in list(ds.coords):
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

    if "height_above_ground" in list(ds.coords) and len(ds.coords["height_above_ground"]) <= 1:
        ds = ds.squeeze("height_above_ground")
        ds = ds.drop("height_above_ground")

    if round_trip_hack:  # see https://github.com/pydata/xarray/issues/5170
        ds = _roundtrip(ds, strict_check=False, copy_filename=round_trip_hack)
    if "valid_time" in list(ds.variables) and "valid_time" not in list(ds.coords):
        ds = ds.set_coords("valid_time")

    for name in list(ds.variables):
        if name not in list(ds.coords):
            ds = ds.rename({name: normalise_string(name, convention="cf")})

    lead_time = "lead_time"
    for name, da in ds.data_vars.items():
        method = CF_CELL_METHODS[name]
        if method is not None:
            da.attrs["cell_method"] = f"{lead_time}: {method}"
        else:
            logging.warn(f"no cell method known for {name}")

    return ds


# replaced by merger='merge()'
# class S2sVariableMerger:
#     def __init__(self, options=None):
#         self.options = options if options is not None else {}
#
#     def to_xarray(self, paths, **kwargs):
#         dslist = [xr.open_dataset(path) for path in paths]
#         return xr.merge(dslist)


class S2sMerger:
    def __init__(self, engine, concat_dim="forecast_time", options=None):
        self.engine = engine
        self.concat_dim = concat_dim
        self.options = options if options is not None else {}

    def to_xarray(self, paths, **kwargs):
        return xr.open_mfdataset(
            paths,
            engine=self.engine,
            preprocess=ensure_naming_conventions,
            concat_dim=self.concat_dim,
            combine="nested",
            **self.options,
        )
