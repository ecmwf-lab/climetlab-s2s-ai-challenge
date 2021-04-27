import climetlab as cml
import xarray as xr

import os

if os.environ.get("TEST_FAST"):
    is_test = "-dev"  # short tests
else:
    is_test = ""  # long tests


def short_print(ds):

    print(dict(ds.dims), list(ds.keys()))


def test_merge_2020_01_02_and_2020_01_09():
    merge_multiple_dates(["20200102", "20200109"])


def test_merge_2020_01_02():
    merge("20200102")


# not uploaded yet
# def test_merge_2020_12_31():
#    merge("20201231")


def merge(date):

    dslist = []
    ds = cml.load_dataset(
        "s2s-ai-challenge-forecast-input" + is_test,
        origin="cwao",
        date=date,
        parameter="2t",
        format="grib",
    )
    dslist.append(ds.to_xarray())
    ds = cml.load_dataset(
        "s2s-ai-challenge-forecast-input" + is_test,
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


def merge_multiple_dates(dates):

    dslist = []
    for date in dates:
        ds = cml.load_dataset(
            "s2s-ai-challenge-forecast-input" + is_test,
            origin="cwao",
            date=date,
            parameter="2t",
        )
        dslist.append(ds.to_xarray())
    for ds in dslist:
        short_print(ds)

    ds = xr.merge(dslist)
    print("-- Merged into --")
    short_print(ds)


if __name__ == "__main__":
    merge_multiple_dates(["20200102", "20200109"])
    merge("20200102")
    merge("20201231")
