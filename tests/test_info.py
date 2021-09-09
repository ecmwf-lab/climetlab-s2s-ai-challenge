#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import pandas as pd

from climetlab_s2s_ai_challenge.info import Info


def test_info():
    for n in (
        "ncep-hindcast-only",
        "test-input-dev",
        "training-input",
        "test-input",
        "training-input-dev",
    ):
        info = Info(n)
        print(info)


def test_get_param_list():

    lst = Info("training-input").get_param_list(origin="ncep", fctype="hindcast")
    assert len(lst) == 19
    assert lst[0] == "t2m"
    assert lst[1] == "siconc"
    assert lst[-1] == "v"

    lst = Info("training-input").get_param_list(origin="ecmwf")
    assert len(lst) == 20

    lst = Info("training-input-dev").get_param_list(origin="ecmwf")
    assert len(lst) == 5


def test_get_all_dates():

    lst = Info("training-input")._get_config("alldates", origin="ncep")
    assert len(lst) == 51
    assert lst[0] == pd.Timestamp("2010-01-07 00:00:00", freq="W-THU")
    assert lst[1] == pd.Timestamp("2010-01-14 00:00:00", freq="W-THU")
    assert lst[-1] == pd.Timestamp("2010-12-23 00:00:00", freq="W-THU")

    lst = Info("training-input-dev")._get_config("alldates", origin="ncep")
    assert len(lst) == 6


if __name__ == "__main__":
    # test_read_2t_ecmwf_grib_cf_convention()
    test_info()
