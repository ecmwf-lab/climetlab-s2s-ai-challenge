# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import os

import climetlab as cml
import climetlab.utils
import climetlab.utils.conventions
import pandas
import yaml

from . import (
    ALIAS_DATASETNAMES,
    ALIAS_FCTYPE,
    ALIAS_ORIGIN,
    DATA_VERSION,
    PATTERN_GRIB,
    PATTERN_NCDF,
)


class Info:
    def __init__(self, dataset):
        if "_" in dataset and dataset not in ALIAS_DATASETNAMES.keys():
            raise ValueError(f'Cannot find {dataset}. Did you mean {dataset.replace("_", "-")} maybe ?')
        dataset = ALIAS_DATASETNAMES[dataset]
        self.dataset = dataset

        filename = self.dataset.replace("-", "_") + ".yaml"
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(path) as f:
            self.config = yaml.load(f.read(), Loader=yaml.SafeLoader)
            for k, v in self.config.items():
                if "alldates" in v:
                    v["alldates"] = pandas.date_range(**v["alldates"])

        self.fctype = self._guess_fctype()

    def _guess_fctype(self):
        keys = self.config.keys()
        fctypes = [k.split("-")[-1] for k in keys]
        fctypes = list(set(fctypes))  # make unique
        assert len(fctypes) == 1
        return fctypes[0]

    def _get_cf_name(self, param):
        return cml.utils.conventions.normalise_string(param, convention="cf")

    # TODO add _
    def get_category_param(self, param):
        if param in "t2m/siconc/2t/sst/sm20/sm100/st20/st100/ci/rsn/tcc/tcw".split("/"):
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

    def _get_s3path_grib(self, origin, fctype, parameter, date, url="s3://", version=DATA_VERSION):
        origin = ALIAS_ORIGIN[origin]
        fctype = ALIAS_FCTYPE[fctype]
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

    def _get_s3path_netcdf(self, origin, fctype, parameter, date, url="s3://", version=DATA_VERSION):
        origin = ALIAS_ORIGIN[origin]
        fctype = ALIAS_FCTYPE[fctype]
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

    def _get_config(self, key, origin, fctype=None, date=None, param=None):
        origin = ALIAS_ORIGIN[origin]

        if fctype is None:
            fctype = self.fctype
        fctype = ALIAS_FCTYPE[fctype]

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

    def get_param_list(self, origin, fctype=None):
        lst = self._get_config("param", origin, fctype)
        lst = [self._get_cf_name(p) for p in lst]
        return lst
