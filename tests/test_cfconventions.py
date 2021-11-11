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
import pytest

is_test = os.environ.get("TEST_FAST", False)


def get_dataset(format, param):
    return cml.load_dataset(
        "s2s-ai-challenge-test-input",
        dev=is_test,
        origin="ecmwf",
        date="20200102",
        parameter=param,
        format=format,
    )


@pytest.mark.skipif(not os.environ.get("TEST_FAST", None) is None, reason="siconc/ci not in dev dataset")
@pytest.mark.parametrize("param", ["2t", "ci", "t2m", ["t2m", "ci"]])
def test_read_grib_to_xarray(param):
    dsgrib = get_dataset("grib", param)
    dsgrib = dsgrib.to_xarray()
    dsnetcdf = get_dataset("netcdf", param).to_xarray()
    print(dsgrib)
    print(dsnetcdf)
    assert dsgrib.attrs == dsgrib.attrs


@pytest.mark.parametrize("param", ["2t", "t2m"])
def test_read_grib_to_xarray_2(param):
    dsgrib = get_dataset("grib", param)
    dsgrib = dsgrib.to_xarray()
    dsnetcdf = get_dataset("netcdf", param).to_xarray()
    print(dsgrib)
    print(dsnetcdf)
    assert dsgrib.attrs == dsgrib.attrs


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
