import climetlab as cml
import climetlab.utils
import climetlab.utils.conventions
import pandas

from . import ALIAS_FCTYPE, ALIAS_ORIGIN, DATA_VERSION, PATTERN_GRIB, PATTERN_NCDF

ALIAS_DATASETNAMES = {
    "hindcast-input": "training-input",
    "forecast-input": "test-input",
    "hindcast-input-dev": "training-input-dev",
    "forecast-input-dev": "test-input-dev",
    "hindcast-like-observations": "training-output-reference",
    "forecast-like-observations": "test-output-reference",
    "forecast-benchmark": "test-output-benchmark",
}


class Info:
    def __init__(self, dataset):
        import os

        import yaml

        #        dataset = ALIAS_DATASETNAMES.get(dataset, dataset)
        self.dataset = dataset

        filename = self.dataset.replace("-", "_") + ".yaml"
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(path) as f:
            self.config = yaml.load(f.read(), Loader=yaml.SafeLoader)
            for k, v in self.config.items():
                if "alldates" in v:
                    v["alldates"] = pandas.date_range(**v["alldates"])

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

    def _get_config(self, key, origin, fctype, date=None, param=None):
        origin = ALIAS_ORIGIN[origin]
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
