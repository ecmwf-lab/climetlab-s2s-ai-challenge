#!/usr/bin/env python3

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

if os.environ.get("TEST_FAST"):
    is_test = "-dev"  # short tests
else:
    is_test = ""  # long tests


def get_dataset(format):
    return cml.load_dataset(
        "s2s-ai-challenge-forecast-input" + is_test,
        origin="cwao",
        date="20200102",
        parameter="2t",
        format=format,
    )


def test_read_grib_to_xarray():
    dsgrib = get_dataset("grib")
    dsgrib = dsgrib.to_xarray()
    dsnetcdf = get_dataset("netcdf").to_xarray()
    print(dsgrib)
    print(dsnetcdf)
    assert dsgrib.attrs == dsgrib.attrs


if __name__ == "__main__":
    test_read_grib_to_xarray()
