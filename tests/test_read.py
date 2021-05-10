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


def _generic_test_read(
    parameter,
    origin,
    format,
    date="20200102",
    fctype="forecast",
    datasetname="s2s-ai-challenge-forecast-input" + is_test,
):
    ds = cml.load_dataset(
        datasetname,
        origin=origin,
        date=date,
        parameter=parameter,
        format=format,
        fctype=fctype,
        #        version='0.1.50'
    )
    xds = ds.to_xarray()
    print(xds)


def test_read_tp_ecmwf_grib__():
    _generic_test_read(parameter="tp", origin="ecmwf", format="grib")


def test_read_domain_name():
    _generic_test_read(
        parameter="tp", origin="ecmwf", format="grib", datasetname="s2s-ai-challenge-forecast-input" + is_test
    ),


def test_read_ml_name():
    _generic_test_read(
        parameter="tp", origin="ecmwf", format="grib", datasetname="s2s-ai-challenge-test-input" + is_test
    ),


def test_read_tp_ecmwf_netcdf():
    _generic_test_read(parameter="tp", origin="ecmwf", format="netcdf")


def test_read_tp_cwao_grib__():
    _generic_test_read(parameter="tp", origin="cwao", format="grib")


def test_read_tp_cwao_netcdf():
    _generic_test_read(parameter="tp", origin="cwao", format="netcdf")


def test_read_tp_kwbc_grib__():
    _generic_test_read(parameter="tp", origin="kwbc", format="grib")


def test_read_tp_kwbc_netcdf():
    _generic_test_read(parameter="tp", origin="kwbc", format="netcdf")


def test_read_tp_and_2t_ecmwf_netcdf():
    _generic_test_read(parameter=["tp", "2t"], origin="ecmwf", format="grib")


def test_read_tp_and_2t_ecmwf_grib__():
    _generic_test_read(parameter=["tp", "2t"], origin="ecmwf", format="netcdf")


def test_read_2t_ecmwf_grib_mars_convention():
    _generic_test_read(parameter="2t", origin="ecmwf", format="grib")


def test_read_2t_ecmwf_grib_cf_convention():
    _generic_test_read(parameter="t2m", origin="ecmwf", format="grib")


# not yet uploaded
# def test_read_2dates_cwao():
#    _generic_test_read(
#        parameter="t2m", origin="cwao", format="grib", date=["20200102", "20201231"]
#    )


# not yet uploaded
# def test_read_2dates_kwbc():
#    _generic_test_read(
#        parameter="t2m", origin="kwbc", format="grib", date=["20200102", "20201231"]
#    )


# not yet uploaded
# def test_read_hindcast_grib():
#    _generic_test_read(parameter="rsn", origin="ecmwf", format="grib")


# not yet uploaded
# def test_read_hindcast_netcdf():
#    _generic_test_read(parameter="rsn", origin="ecmwf", format="netcdf")


# def test_read_hc():
#    ds = cml.load_dataset("s2s-ai-challenge", date="20200102", hindcast=True)
#    xds = ds.to_xarray()
#    print(xds)
#
#
# def test_read_rt_2dates():
#    ds = cml.load_dataset("s2s-ai-challenge", date=["20200102", "20200102"])
#    xds = ds.to_xarray()
#    print(xds)
#
#    sst = xds.sel()
#

if __name__ == "__main__":
    # test_read_2t_ecmwf_grib_cf_convention()
    test_read_tp_ecmwf_grib__()
