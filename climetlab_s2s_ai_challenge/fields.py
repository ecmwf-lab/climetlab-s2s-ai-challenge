import climetlab as cml
import pandas as pd
import xarray as xr
from climetlab.normalize import DateListNormaliser, normalize_args
from climetlab.utils.conventions import normalise_string

from climetlab_s2s_ai_challenge.info import Info

from . import (  # ALIAS_MARSORIGIN,
    ALIAS_FCTYPE,
    ALIAS_ORIGIN,
    CF_CELL_METHODS,
    DATA,
    DATA_VERSION,
    PATTERN_GRIB,
    PATTERN_NCDF,
    PATTERN_ZARR,
    URL,
)
from .s2s_dataset import S2sDataset, add_attributes


class FieldS2sDataset(S2sDataset):

    dataset = None

    @normalize_args(parameter="variable-list(cf)")
    def __init__(self, origin, version, dataset, fctype, parameter, date=None):
        self.origin = ALIAS_ORIGIN[origin.lower()]
        self.fctype = ALIAS_FCTYPE[fctype.lower()]
        self.version = version
        self.dataset = dataset
        self.info = Info(dataset)
        self.default_datelist = self.info._get_config("alldates", origin, fctype)
        self.parameter = parameter
        self.date = self.parse_date(date)
        self._load()

    def parse_date(self, date):
        if date is None:
            date = self.default_datelist
        date = DateListNormaliser("%Y%m%d")(date)
        for d in date:
            pd_date = pd.to_datetime(d)
            if pd_date not in self.default_datelist:
                raise ValueError(f"{d} is not in the available list of dates {self.default_datelist}")
        return date

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
            parameter=self.parameter,
            fctype=self.fctype,
            date=self.date,
        )
        return request


def roundtrip(ds, strict_check=True, copy_filename=None, verbose=False):
    import xarray as xr

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
        ds = roundtrip(ds, strict_check=False, copy_filename=round_trip_hack)
    if "valid_time" in list(ds.variables) and "valid_time" not in list(ds.coords):
        ds = ds.set_coords("valid_time")

    for name in list(ds.variables):
        ds = ds.rename({name: normalise_string(name, convention="cf")})

    lead_time = "lead_time"
    for name, da in ds.data_vars.items():
        method = CF_CELL_METHODS[name]
        if method is not None:
            da.attrs["cell_method"] = f"{lead_time}: {method}"
        else:
            import logging

            logging.warn(f"no cell method known for {name}")

    return ds


class S2sMerger:
    def __init__(self, engine, concat_dim="forecast_time", options=None):
        self.engine = engine
        self.concat_dim = concat_dim
        self.options = options if options is not None else {}

    def merge(self, paths, **kwargs):
        return xr.open_mfdataset(
            paths,
            engine=self.engine,
            preprocess=ensure_naming_conventions,
            concat_dim=self.concat_dim,
            combine="nested",
            **self.options,
        )


class S2sDatasetGRIB(FieldS2sDataset):
    def _load(self):
        options = {
            "chunks": {"time": 1, "latitude": None, "longitude": None, "number": 1, "step": 1},
            "backend_kwargs": {
                "squeeze": False,
                "time_dims": ["time", "step"],  # this is the default in cfgrib
            },
        }

        request = self._make_request()
        self.source = cml.load_source(
            "url-pattern", PATTERN_GRIB, request, merger=S2sMerger(engine="cfgrib", options=options)
        )


class S2sDatasetNETCDF(FieldS2sDataset):
    def _load(self):
        request = self._make_request()
        self.source = cml.load_source("url-pattern", PATTERN_NCDF, request, merger=S2sMerger(engine="netcdf4"))


class S2sDatasetZARR(FieldS2sDataset):
    def _load(self, *args, **kwargs):

        from climetlab.utils.patterns import Pattern

        request = self._make_request(*args, **kwargs)
        request.pop("date")

        urls = Pattern(PATTERN_ZARR).substitute(request)

        self.source = cml.load_source("zarr-s3", urls)


CLASSES = {"grib": S2sDatasetGRIB, "netcdf": S2sDatasetNETCDF, "zarr": S2sDatasetZARR}


def training_input(format="grib", origin="ecmwf", fctype="hindcast", version=DATA_VERSION, *args, **kwargs):
    return CLASSES[format](*args, origin=origin, version=version, dataset="training-input", fctype=fctype, **kwargs)


add_attributes(training_input, S2sDataset)


def training_input_dev(format="grib", origin="ecmwf", fctype="hindcast", version=DATA_VERSION, *args, **kwargs):
    return CLASSES[format](*args, origin=origin, version=version, dataset="training-input-dev", fctype=fctype, **kwargs)


add_attributes(training_input_dev, S2sDataset)


def test_input(format="grib", origin="ecmwf", fctype="forecast", version=DATA_VERSION, *args, **kwargs):
    return CLASSES[format](*args, origin=origin, version=version, dataset="test-input", fctype=fctype, **kwargs)


add_attributes(test_input, S2sDataset)


def test_input_dev(format="grib", origin="ecmwf", fctype="forecast", version=DATA_VERSION, *args, **kwargs):
    return CLASSES[format](*args, origin=origin, version=version, dataset="test-input-dev", fctype=fctype, **kwargs)


add_attributes(test_input_dev, S2sDataset)


hindcast_input = training_input
forecast_input = test_input
hindcast_input_dev = training_input_dev
forecast_input_dev = test_input_dev
