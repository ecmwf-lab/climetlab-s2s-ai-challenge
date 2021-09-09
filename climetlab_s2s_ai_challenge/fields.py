import climetlab as cml
import pandas as pd
from climetlab.normalize import DateListNormaliser

from . import (  # ALIAS_MARSORIGIN,
    ALIAS_FCTYPE,
    ALIAS_ORIGIN,
    DATA,
    DATA_VERSION,
    PATTERN_GRIB,
    PATTERN_NCDF,
    PATTERN_ZARR,
    URL,
    S2sDataset,
)
from .extra import cf_conventions
from .info import Info
from .s2s_mergers import S2sMerger


class FieldS2sDataset(S2sDataset):

    dataset = None

    def __init__(self, origin, fctype, parameter, format, version=DATA_VERSION, date=None):
        parameter = cf_conventions(parameter)
        self.origin = ALIAS_ORIGIN[origin.lower()]
        self.fctype = ALIAS_FCTYPE[fctype.lower()]
        self.version = version
        self.default_datelist = self.get_all_reference_dates()
        self.parameter = parameter
        self.date = self.parse_date(date)
        self.format = {
            "grib": Grib(),
            "netcdf": Netcdf(),
            "zarr": Zarr(),
        }[format]

        request = self._make_request()
        self.source = self.format._load(request)

    @classmethod
    def cls_get_all_reference_dates(cls, origin, fctype):
        return cls._info()._get_config("alldates", origin=origin, fctype=fctype)

    def get_all_reference_dates(self):
        return self._info()._get_config("alldates", origin=self.origin, fctype=self.fctype)

    @classmethod
    def _info(cls):
        print(cls.dataset)
        return Info(cls.dataset)

    def parse_date(self, date):
        if date is None:
            date = self.default_datelist
        date = DateListNormaliser("%Y%m%d")(date)
        for d in date:
            pd_date = pd.to_datetime(d)
            if pd_date not in self.default_datelist:
                raise ValueError(f"{d} is not in the available list of dates {self.default_datelist}")
        return date

    def _make_request(self):
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


class Grib:
    def _load(self, request):
        options = {
            "chunks": {"time": 1, "latitude": None, "longitude": None, "number": 1, "step": 1},
            "backend_kwargs": {
                "squeeze": False,
                "time_dims": ["time", "step"],  # this is the default in cfgrib
            },
        }

        return cml.load_source("url-pattern", PATTERN_GRIB, request, merger=S2sMerger(engine="cfgrib", options=options))


class Netcdf:
    def _load(self, request):
        return cml.load_source("url-pattern", PATTERN_NCDF, request, merger=S2sMerger(engine="netcdf4"))


class Zarr:
    def _load(self, request, *args, **kwargs):

        from climetlab.utils.patterns import Pattern

        request.pop("date")

        urls = Pattern(PATTERN_ZARR).substitute(request)

        return cml.load_source("zarr-s3", urls)


class TrainingInput(FieldS2sDataset):
    dataset = "training-input"

    def __init__(self, origin="ecmwf", format="netcdf", fctype="hindcast", **kwargs):
        super().__init__(format=format, origin=origin, fctype=fctype, **kwargs)


class TrainingInputDev(TrainingInput):
    dataset = "training-input-dev"


class TestInput(FieldS2sDataset):
    dataset = "test-input"

    def __init__(self, origin="ecmwf", format="netcdf", fctype="forecast", **kwargs):
        super().__init__(format=format, origin=origin, fctype=fctype, **kwargs)


class TestInputDev(TestInput):
    dataset = "test-input-dev"
