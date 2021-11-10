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


def get_dataset(origin, param):
    return cml.load_dataset(
        "s2s-ai-challenge-test-input",
        dev=is_test,
        origin=origin,
        date="20200102",
        parameter=param,
        format="netcdf",
    )


@pytest.mark.parametrize(
    "args",
    [
        ["ecmwf", "t2m"],
        ["eccc", "t2m"],
    ],
)
def test_availabilty_1(args):
    print(get_dataset(origin=args[0], param=args[1]).to_xarray())


@pytest.mark.parametrize(
    "args",
    [
        ["eccc", "st100"],
        ["ncep", "rsn"],
    ],
)
def test_availability_2(args):
    with pytest.raises(ValueError):
        print(get_dataset(origin=args[0], param=args[1]).to_xarray())


def test_availability_3():
    cml.load_dataset(
        "s2s-ai-challenge-training-input", date=[20100107], origin="ncep", parameter="tp", format="netcdf"
    ).to_xarray()


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
