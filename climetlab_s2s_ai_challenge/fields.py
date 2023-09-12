# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import climetlab as cml
from climetlab.decorators import availability, normalize

from . import (  # ALIAS_MARSORIGIN,
    ALIAS_FCTYPE,
    DATA,
    DATA_VERSION,
    PATTERN_GRIB,
    PATTERN_NCDF,
    PATTERN_ZARR,
    URL,
    S2sDataset,
)
from .availability import s2s_availability_parser
from .info import Info
from .s2s_mergers import ensure_naming_conventions

PARAMS = [
    "t2m",
    "siconc",
    "gh",
    "lsm",
    "msl",
    "q",
    "rsn",
    "sm100",
    "sm20",
    "sp",
    "sst",
    "st100",
    "st20",
    "t",
    "tcc",
    "tcw",
    "tp",
    "ttr",
    "u",
    "v",
]


class FieldS2sDataset(S2sDataset):
    dataset = None

    @availability("input.yaml", parser=s2s_availability_parser)
    @normalize("origin", ["ecmwf", "eccc", "ncep"], aliases={"ecmf": "ecmwf", "cwao": "eccc", "kwbc": "ncep"})
    @normalize("fctype", ["forecast", "hindcast"], aliases=ALIAS_FCTYPE)
    @normalize("parameter", ["ALL"] + PARAMS, multiple=True, aliases={"2t": "t2m", "ci": "siconc"})
    # @normalize("date", multiple=True)
    @normalize("date", "date-list(%Y%m%d)")
    def __init__(self, origin, fctype, format, dev, parameter="ALL", version=DATA_VERSION, date=None):
        self._development_dataset = dev
        self.origin = origin
        self.fctype = fctype
        self.version = version
        self.format = {
            "grib": Grib(),
            "netcdf": Netcdf(),
            "zarr": Zarr(),
        }[format]
        if date is None:
            date = [d.strftime("%Y%m%d") for d in self.get_all_reference_dates()]
        self.date = date
        if parameter == ["ALL"]:
            parameter = self._info().get_param_list(
                origin=origin,
                fctype=fctype,
            )

        sources = []
        for p in parameter:
            request = self._make_request(p)
            sources.append(self.format._load(request))
        self.source = cml.load_source("multi", sources, merger="merge()")

    def to_xarray(self, *args, **kwargs):
        ds = self.source.to_xarray(*args, **kwargs)
        ds = ensure_naming_conventions(ds)
        return ds

    @classmethod
    def cls_get_all_reference_dates(cls, origin, fctype):
        return cls._info()._get_config("alldates", origin=origin, fctype=fctype)

    def get_all_reference_dates(self):
        return self._info()._get_config("alldates", origin=self.origin, fctype=self.fctype)

    @classmethod
    def _info(cls):
        return Info(cls.dataset)

    def _make_request(self, p):
        dataset = self.dataset
        if self._development_dataset:
            dataset = dataset + "-dev"
        request = dict(
            url=URL,
            data=DATA,
            dataset=dataset,
            origin=self.origin,
            version=self.version,
            parameter=p,
            fctype=self.fctype,
            date=self.date,
        )
        return request


class Grib:
    def _load(self, request):
        return cml.load_source(
            "url-pattern",
            PATTERN_GRIB,
            request,
        )


class Netcdf:
    def _load(self, request):
        return cml.load_source(
            "url-pattern",
            PATTERN_NCDF,
            request,
            merger="concat(concat_dim=forecast_time)",
            # maybe need to add combine="nested" in xarray merge
        )


class Zarr:
    def _load(self, request, *args, **kwargs):
        from climetlab.utils.patterns import Pattern

        request.pop("date")

        urls = Pattern(PATTERN_ZARR).substitute(request)

        return cml.load_source("zarr-s3", urls)


class TrainingInput(FieldS2sDataset):
    dataset = "training-input"

    def __init__(self, origin="ecmwf", format="netcdf", fctype="hindcast", dev=False, **kwargs):
        super().__init__(format=format, origin=origin, fctype=fctype, dev=dev, **kwargs)


class TestInput(FieldS2sDataset):
    dataset = "test-input"

    def __init__(self, origin="ecmwf", format="netcdf", fctype="forecast", dev=False, **kwargs):
        super().__init__(format=format, origin=origin, fctype=fctype, dev=dev, **kwargs)
