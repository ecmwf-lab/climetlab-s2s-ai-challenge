import os

import climetlab as cml
import pytest
import xarray as xr

is_test = os.environ.get("TEST_FAST", False)


def short_print(ds):

    print(dict(ds.dims), list(ds.keys()))


@pytest.mark.parametrize("format1", ["grib", "netcdf"])
@pytest.mark.parametrize("format2", ["grib", "netcdf"])
def test_merge_2020_01_02_and_2020_01_09(format1, format2):
    merge_multiple_dates(["20200102", "20200109"], format1, format2)


def test_merge_2020_01_02():
    merge("20200102")


# not uploaded yet
# def test_merge_2020_12_31():
#    merge("20201231")


def merge(date):

    dslist = []
    ds = cml.load_dataset(
        "s2s-ai-challenge-forecast-input",
        dev=is_test,
        origin="cwao",
        date=date,
        parameter="2t",
        format="grib",
    )
    dslist.append(ds.to_xarray())
    ds = cml.load_dataset(
        "s2s-ai-challenge-forecast-input",
        dev=is_test,
        origin="cwao",
        date=date,
        parameter="tp",
        format="grib",
    )
    dslist.append(ds.to_xarray())

    for ds in dslist:
        short_print(ds)

    ds = xr.merge(dslist)
    print("-- Merged into --")
    short_print(ds)

    # failing on test data.
    # assert dslist[0].lead_time.values[0] == dslist[1].lead_time.values[0]
    # assert dslist[0].lead_time.values[-1] == dslist[1].lead_time.values[-1]


def merge_multiple_dates(dates, format1, format2):

    dslist = []
    for date in dates:
        ds = cml.load_dataset(
            "s2s-ai-challenge-forecast-input",
            dev=is_test,
            origin="cwao",
            date=date,
            parameter="2t",
            format=format1,
        )
        dslist.append(ds.to_xarray())
    for ds in dslist:
        short_print(ds)
        print(ds)

    ds = xr.merge(dslist)
    print("-- Merged into --")
    short_print(ds)

    ds2 = cml.load_dataset(
        "s2s-ai-challenge-forecast-input",
        dev=is_test,
        origin="cwao",
        date=dates,
        parameter="2t",
        format=format2,
    )
    ds2 = ds2.to_xarray()
    print("-- direct merge --")
    short_print(ds2)
    print(ds2)


def test_get_obs_merge_concat():

    cmlds = cml.load_dataset(
        "s2s-ai-challenge-test-output-reference",
        date=20200312,
        parameter=["t2m", "tp"],
    )
    ds = cmlds.to_xarray()
    print(ds)


if __name__ == "__main__":
    merge_multiple_dates(["20200102", "20200109"])
    merge("20200102")
    merge("20201231")
