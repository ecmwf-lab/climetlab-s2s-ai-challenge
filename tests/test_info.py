#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

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


if __name__ == "__main__":
    # test_read_2t_ecmwf_grib_cf_convention()
    test_info()
